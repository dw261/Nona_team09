import hashlib
import hmac
import json
import re
import secrets
from datetime import timezone as datetime_timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils import timezone

from .models import PhoneVerification


SOLAPI_SEND_URL = 'https://api.solapi.com/messages/v4/send-many/detail'
MAX_VERIFY_ATTEMPTS = 5


def normalize_phone_number(phone_number):
    return re.sub(r'[\s-]', '', phone_number.strip())


def validate_phone_number(phone_number):
    normalized = normalize_phone_number(phone_number)
    if not normalized.isdigit() or len(normalized) not in (10, 11):
        raise ValidationError('\uc804\ud654\ubc88\ud638 \ud615\uc2dd\uc774 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.')
    return normalized


def generate_verification_code():
    return f'{secrets.randbelow(900000) + 100000}'


def create_solapi_auth_header():
    if not settings.SMS_API_KEY or not settings.SMS_API_SECRET:
        raise ImproperlyConfigured('SMS API key and secret are required.')

    date_time = timezone.now().astimezone(datetime_timezone.utc).isoformat().replace('+00:00', 'Z')
    salt = secrets.token_hex(16)
    signature = hmac.new(
        settings.SMS_API_SECRET.encode(),
        f'{date_time}{salt}'.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f'HMAC-SHA256 apiKey={settings.SMS_API_KEY}, date={date_time}, salt={salt}, signature={signature}'


def send_sms(to, text):
    if not settings.SMS_SENDER:
        raise ImproperlyConfigured('SMS sender phone number is required.')

    payload = {
        'message': {
            'to': to,
            'from': settings.SMS_SENDER,
            'text': text,
        }
    }
    request = Request(
        SOLAPI_SEND_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': create_solapi_auth_header(),
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        detail = error.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'SMS API request failed: {error.code} {detail}') from error
    except URLError as error:
        raise RuntimeError('SMS API connection failed.') from error


def send_phone_verification(phone_number):
    normalized = validate_phone_number(phone_number)
    latest = PhoneVerification.objects.filter(phone_number=normalized).order_by('-created_at').first()
    now = timezone.now()

    if latest and (now - latest.last_sent_at).total_seconds() < settings.SMS_RESEND_COOLDOWN_SECONDS:
        raise ValidationError('\uc778\uc99d\ubc88\ud638\ub97c \ub108\ubb34 \ube60\ub974\uac8c \uc694\uccad\ud588\uc2b5\ub2c8\ub2e4. \uc7a0\uc2dc \ud6c4 \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \uc8fc\uc138\uc694.')

    code = generate_verification_code()
    verification = PhoneVerification.objects.create(
        phone_number=normalized,
        code_hash=make_password(code),
        expires_at=now + timezone.timedelta(seconds=settings.SMS_VERIFICATION_TTL_SECONDS),
    )
    send_sms(normalized, f'[NONA] \uc778\uc99d\ubc88\ud638\ub294 {code}\uc785\ub2c8\ub2e4.')
    return verification


def verify_phone_code(phone_number, code):
    normalized = validate_phone_number(phone_number)
    verification = PhoneVerification.objects.filter(phone_number=normalized).order_by('-created_at').first()

    if verification is None:
        raise ValidationError('\uc778\uc99d\ubc88\ud638\ub97c \uba3c\uc800 \uc694\uccad\ud574 \uc8fc\uc138\uc694.')
    if verification.is_verified:
        return verification
    if verification.is_expired:
        raise ValidationError('\uc778\uc99d\ubc88\ud638\uac00 \ub9cc\ub8cc\ub418\uc5c8\uc2b5\ub2c8\ub2e4.')
    if verification.attempts >= MAX_VERIFY_ATTEMPTS:
        raise ValidationError('\uc778\uc99d \uc2dc\ub3c4 \ud69f\uc218\ub97c \ucd08\uacfc\ud588\uc2b5\ub2c8\ub2e4.')

    verification.attempts += 1
    verification.save(update_fields=['attempts'])

    if not check_password(str(code).strip(), verification.code_hash):
        raise ValidationError('\uc778\uc99d\ubc88\ud638\uac00 \uc77c\uce58\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.')

    verification.mark_verified()
    return verification
