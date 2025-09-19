# O2RUN Finisher Certificate Generator

Flask + Pillow app that overlays **이름 / 배번 / 코스 / 날짜** on your certificate template (`static/base.png`) and returns a PNG.

## 0) 로컬에서 먼저 실행
```bash
pip install -r requirements.txt
python app.py
# 브라우저: http://127.0.0.1:5000/
```

- 같은 Wi‑Fi의 휴대폰 접속: 서버가 0.0.0.0:5000 에 바인딩됩니다. 방화벽 허용 필요.
- QR: `http://<PC-IP>:5000/qr`  (또는 커스텀 링크 QR: `/qr?link=https://example.com`)

---

## 1) GitHub에 업로드 (최초 1회)

1. 새 저장소 만들기 (예: `o2run-cert`)
2. 터미널에서 프로젝트 폴더로 이동 후:
```bash
git init
git add .
git commit -m "Initial commit: O2RUN cert generator"
git branch -M main
git remote add origin https://github.com/<YOUR_ID>/o2run-cert.git
git push -u origin main
```
> ⚠️ `<YOUR_ID>`는 본인 계정으로 바꾸세요.

---

## 2A) Render에 배포 (쉬움 / 무료티어 가능)

이 저장소에는 **`render.yaml` + `Procfile`** 이 포함되어 있어 클릭 몇 번이면 배포됩니다.

1. https://render.com → New + → **Blueprint** 선택 → GitHub 연동
2. 방금 만든 `o2run-cert` 리포 선택
3. 서비스 이름 확인 (예: `o2run-cert`) → **Free plan** 선택 → **Deploy**  
   - 빌드: `pip install -r requirements.txt`
   - 시작: `gunicorn app:app --bind 0.0.0.0:$PORT` (Procfile에 정의)
4. 배포 완료 → 제공된 URL 복사 (예: `https://o2run-cert.onrender.com/`)

### (선택) 행사용 QR 미리 만들기
```bash
python tools/make_qr.py https://o2run-cert.onrender.com/ o2run-form-qr.png
```
- 또는 배포 서버에서 `/qr` 접속 → PNG 저장

---

## 2B) Google Cloud Run 배포 (안정 / 확장성 좋음)

1. GCP 프로젝트 생성 및 빌링 활성화
2. Cloud Build/Run API 활성화
3. 터미널에서:
```bash
gcloud auth login
gcloud config set project <PROJECT_ID>

gcloud builds submit --tag gcr.io/<PROJECT_ID>/o2run-cert
gcloud run deploy o2run-cert   --image gcr.io/<PROJECT_ID>/o2run-cert   --platform managed   --allow-unauthenticated   --region asia-northeast3
```
4. 배포 URL(예: `https://o2run-cert-xxxx.a.run.app/`)을 행사 QR로 사용

---

## 폰트(한글 가독성)
- `static/fonts/` 폴더에 `NotoSansKR-Regular.ttf` 등 한글 폰트를 넣으면 자동 인식합니다.

## 헬스체크
- `/healthz` → 200 OK면 정상

## 커스텀 QR
- `/qr?link=<URL>` 형태로 어떤 링크든 QR PNG 생성
- 로컬 테스트: `http://127.0.0.1:5000/qr?link=https://o2run.org`

## 템플릿 교체
- `static/base.png` 를 교체하면 됩니다. 박스 자동 감지 로직이 기본 템플릿에 맞춰져 있으니 레이아웃이 크게 바뀌면 `detect_boxes()`의 fallback 좌표를 수정하세요.

## 라이선스
MIT
