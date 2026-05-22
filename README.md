# Nona_team09
삼육대 &amp; 서울여대 토이 프로젝트

## 작업 시작할 때마다

# 최신 코드 받기
git pull origin main

# 가상환경 활성화
source venv/bin/activate      # Mac/Linux
venv\Scripts\Activate.ps1    # Windows PowerShell

# 패키지 새로 추가됐을 수 있으니 확인
pip install -r requirements.txt

# 마이그레이션 새로 추가됐을 수 있으니 확인
python manage.py migrate

---

## 주의사항
- .env 파일은 절대 GitHub에 올리지 말 것
- 패키지 새로 설치했으면 반드시 pip freeze > requirements.txt 후 커밋
- 모델 변경했으면 반드시 python manage.py makemigrations 후 커밋