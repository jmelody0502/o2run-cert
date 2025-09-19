# O2RUN Finisher Certificate Generator (Fixed)

Flask + Pillow app that overlays **이름 / 배번 / 코스 / 날짜** on your certificate template and returns a PNG.

## Quick start
```bash
pip install -r requirements.txt
python app.py
# http://127.0.0.1:5000/
```

## Deploy
- Render: use `render.yaml` (Blueprint) or `Procfile`
- Cloud Run: use `Dockerfile`
- Healthcheck: `/healthz`
- QR: `/qr?link=<PUBLIC_URL>/`

## Fonts
Put a Korean font like `NotoSansKR-Regular.ttf` into `static/fonts/` for better Hangul rendering.
