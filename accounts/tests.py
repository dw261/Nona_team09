from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch

from accounts.forms import SignupForm
from accounts.models import PhoneVerification, Profile


class ProfileSignalTests(TestCase):
    def test_profile_is_created_for_new_user(self):
        user = User.objects.create_user(username='01055556666', password='pass12345')

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.phone_number, user.username)
        self.assertEqual(profile.nickname, user.username)

    def test_signup_form_updates_signal_created_profile(self):
        form = SignupForm(data={
            'phone_number': '01077778888',
            'nickname': 'nona',
            'password1': 'pass12345!@',
            'password2': 'pass12345!@',
        })

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.phone_number, '01077778888')
        self.assertEqual(profile.nickname, 'nona')


class AccountEntryFlowTests(TestCase):
    def test_root_redirects_anonymous_user_to_welcome(self):
        response = self.client.get('/')

        self.assertRedirects(response, reverse('accounts:welcome'), fetch_redirect_response=False)

    def test_root_redirects_authenticated_user_to_group_list(self):
        user = User.objects.create_user(username='01099990000', password='pass12345')
        self.client.force_login(user)

        response = self.client.get('/')

        self.assertRedirects(response, reverse('posts:group_list'), fetch_redirect_response=False)

    def test_welcome_links_to_phone_page(self):
        response = self.client.get(reverse('accounts:welcome'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('accounts:phone'))

    def test_phone_page_links_existing_user_to_login(self):
        response = self.client.get(reverse('accounts:phone'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('accounts:login'))
        self.assertContains(response, '&#xC774;&#xBBF8; &#xACC4;&#xC815;&#xC774; &#xC874;&#xC7AC;&#xD569;&#xB2C8;&#xB2E4;', html=False)

    @patch('accounts.sms.send_sms')
    def test_phone_page_sends_code_and_redirects_to_code_page(self, send_sms_mock):
        response = self.client.post(reverse('accounts:phone'), {'phone_number': '010-1234-5678'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('accounts:code'))
        self.assertTrue(PhoneVerification.objects.filter(phone_number='01012345678').exists())
        send_sms_mock.assert_called_once()

    def test_code_page_verifies_code_and_redirects_to_signup(self):
        session = self.client.session
        session['pending_phone_number'] = '01012345678'
        session.save()
        PhoneVerification.objects.create(
            phone_number='01012345678',
            code_hash=make_password('123456'),
            expires_at=timezone.now() + timezone.timedelta(minutes=5),
        )

        response = self.client.post(reverse('accounts:code'), {'code': '123456'})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(reverse('accounts:signup')))
        self.assertIn('phone_number=01012345678', response['Location'])

    def test_verify_alias_renders_code_page(self):
        session = self.client.session
        session['pending_phone_number'] = '01012345678'
        session.save()

        response = self.client.get(reverse('accounts:verify'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="code"')
        self.assertContains(response, '01012345678')

    def test_signup_prefills_phone_number_from_query(self):
        response = self.client.get(reverse('accounts:signup'), {'phone_number': '010-1234-5678'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="010-1234-5678"')

    def test_signup_view_requires_verified_phone_number(self):
        response = self.client.post(reverse('accounts:signup'), {
            'phone_number': '01012345678',
            'nickname': 'nona',
            'password1': 'pass12345!@',
            'password2': 'pass12345!@',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '\uc804\ud654\ubc88\ud638 \uc778\uc99d\uc774 \ud544\uc694\ud569\ub2c8\ub2e4.')

    def test_signup_view_accepts_verified_phone_number(self):
        session = self.client.session
        session['verified_phone_number'] = '01012345678'
        session.save()

        response = self.client.post(reverse('accounts:signup'), {
            'phone_number': '01012345678',
            'nickname': 'nona',
            'password1': 'pass12345!@',
            'password2': 'pass12345!@',
        })

        self.assertRedirects(response, reverse('accounts:location'), fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(username='01012345678').exists())

    def test_location_and_complete_pages_require_login_and_render(self):
        user = User.objects.create_user(username='01044445555', password='pass12345')
        self.client.force_login(user)

        location_response = self.client.get(reverse('accounts:location'))
        complete_response = self.client.get(reverse('accounts:complete'))

        self.assertEqual(location_response.status_code, 200)
        self.assertContains(location_response, '현재 위치로 인증하기')
        self.assertEqual(complete_response.status_code, 200)
        self.assertContains(complete_response, '가입이 완료')

    def test_logout_redirects_to_login_page(self):
        user = User.objects.create_user(username='01022223333', password='pass12345')
        self.client.force_login(user)

        response = self.client.post(reverse('accounts:logout'))

        self.assertRedirects(response, reverse('accounts:login'), fetch_redirect_response=False)
