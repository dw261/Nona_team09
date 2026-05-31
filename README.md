# Nona_team09
삼육대 &amp; 서울여대 토이 프로젝트

## 🚀 Project Setup Guide

개발 시작 전 반드시 확인해주세요.


### 📥 작업 시작 전

#### 1. 최신 코드 받기

```bash
git pull origin dev
```

#### 2. 가상환경 활성화

##### Mac / Linux

```bash
source venv/bin/activate
```

##### Windows PowerShell

```powershell
venv\Scripts\activate
```

#### 3. 패키지 설치 확인

새로운 패키지가 추가되었을 수 있으니 실행해주세요.

```bash
pip install -r requirements.txt
```

#### 4. 마이그레이션 적용

새로운 migration 파일이 있을 수 있으니 실행해주세요.

```bash
python manage.py migrate
```

---

### 🌱 브랜치 사용 방법

#### 브랜치 생성

작업 시작 전 반드시 개인 브랜치를 생성해주세요.

```bash
git checkout -b 브랜치명
```

예시:

```bash
git checkout -b feature/login
```

#### 브랜치 변경

다른 브랜치로 이동할 때 사용합니다.

```bash
git checkout 브랜치명
```

예시:

```bash
git checkout dev
```

#### 현재 브랜치 확인

```bash
git branch
```

현재 브랜치 앞에는 `*` 표시가 붙습니다.

---

### 📤 작업 후 Push 방법

#### 1. 변경 파일 확인

```bash
git status
```

#### 2. 파일 추가

전체 추가:

```bash
git add .
```

#### 3. 커밋

```bash
git commit -m "feat: 로그인 기능 추가"
```

##### 커밋 메시지 예시

| 타입 | 설명 |
|---|---|
| feat | 기능 추가 |
| fix | 버그 수정 |
| refactor | 리팩토링 |
| docs | 문서 수정 |
| style | 코드 스타일 수정 |
| chore | 설정 작업 |

#### 4. Push

```bash
git push origin 브랜치명
```

예시:

```bash
git push origin feature/login
```

---

### 🔄 main 최신 코드 가져오기

작업 중 main 브랜치가 업데이트되었을 경우:

```bash
git checkout dev
git pull origin dev
```

다시 작업 브랜치로 이동:

```bash
git checkout 브랜치명
```

main 내용 반영:

```bash
git merge dev
```

---

### ⚠️ 주의사항

- `.env` 파일은 절대 GitHub에 올리지 말 것
- 패키지 새로 설치했으면 반드시 아래 명령어 실행 후 커밋

```bash
pip freeze > requirements.txt
```

- 모델 변경 시 반드시 migration 생성 후 커밋

```bash
python manage.py makemigrations
```

- push 전 오류 없는지 서버 실행 확인 필수

```bash
python manage.py runserver
```

---

## 🛠️ 자주 사용하는 명령어 모음

#### 서버 실행

```bash
python manage.py runserver
```

#### migration 생성

```bash
python manage.py makemigrations
```

#### migration 적용

```bash
python manage.py migrate
```


#### 설치된 패키지 확인

```bash
pip list
```


#### Git 로그 확인

```bash
git log --oneline
```

---
