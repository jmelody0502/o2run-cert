import os, socket
from io import BytesIO
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import qrcode

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_DIR, "static")
BASE_IMG_PATH = os.path.join(STATIC_DIR, "base.png")

app = Flask(__name__)

def get_font(size: int):
    candidates = [
        os.path.join(STATIC_DIR, "fonts", "NotoSansKR-Regular.ttf"),
        os.path.join(STATIC_DIR, "fonts", "Pretendard-Regular.ttf"),
        os.path.join(STATIC_DIR, "fonts", "NanumGothic.ttf"),
        os.path.join(STATIC_DIR, "fonts", "NanumSquare.ttf"),
        os.path.join(STATIC_DIR, "fonts", "NotoSansCJKkr-Regular.otf"),
        "DejaVuSans.ttf"
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()

def detect_boxes(base_img):
    im = base_img.convert("RGB")
    arr = np.array(im)
    h, w, _ = arr.shape
    gray = np.dot(arr[...,:3], [0.299, 0.587, 0.114])
    mask = (gray > 245).astype(np.uint8)
    visited = np.zeros_like(mask, dtype=bool)

    def neighbors(y, x):
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dy==0 and dx==0:
                    continue
                ny, nx = y+dy, x+dx
                if 0 <= ny < h and 0 <= nx < w:
                    yield ny, nx

    regions = []
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if mask[y, x] and not visited[y, x]:
                stack = [(y, x)]
                visited[y, x] = True
                miny, minx = y, x
                maxy, maxx = y, x
                count = 0
                while stack:
                    cy, cx = stack.pop()
                    count += 1
                    if cy < miny: miny = cy
                    if cx < minx: minx = cx
                    if cy > maxy: maxy = cy
                    if cx > maxx: maxx = cx
                    for ny, nx in neighbors(cy, cx):
                        if mask[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((ny, nx))
                area = (maxy-miny+1)*(maxx-minx+1)
                if count > 500 and area > 20000:
                    regions.append((minx, miny, maxx, maxy, count))

    regions_sorted = sorted(regions, key=lambda r: (r[1], r[0]))
    upper_regions = [r for r in regions_sorted if r[3] < int(h*0.8)]
    if len(upper_regions) > 4:
        upper_regions = sorted(upper_regions, key=lambda r: (r[2]-r[0]), reverse=True)[1:]
        upper_regions = sorted(upper_regions, key=lambda r: (r[1], r[0]))
    if len(upper_regions) != 4:
        upper_regions = [
            (156, 430, 434, 541), # name
            (458, 430, 734, 541), # bib
            (156, 558, 434, 669), # course
            (456, 558, 732, 669), # date
        ]
    upper_regions = [(r[0], r[1], r[2], r[3]) for r in upper_regions]
    upper_regions = sorted(upper_regions, key=lambda r: (r[1], r[0]))
    return upper_regions

def text_bbox_size(draw, text, font):
    try:
        l, t, r, b = draw.textbbox((0,0), text, font=font)
        return (r - l, b - t)
    except Exception:
        return draw.textsize(text, font=font)

def fit_text_in_box(draw, text, box, max_size=64, min_size=18, padding=18):
    x1, y1, x2, y2 = box
    box_w = max(1, x2 - x1 - padding*2)
    box_h = max(1, y2 - y1 - padding*2)

    lo, hi = min_size, max_size
    best = get_font(min_size)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = get_font(mid)
        tw, th = text_bbox_size(draw, text, f)
        if tw <= box_w and th <= box_h:
            best = f
            lo = mid + 1
        else:
            hi = mid - 1

    tw, th = text_bbox_size(draw, text, best)
    tx = x1 + (x2 - x1 - tw)//2
    ty = y1 + (y2 - y1 - th)//2
    return best, (tx, ty)

@app.route("/", methods=["GET"])
def form():
    return render_template("form.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        name = (request.form.get("name") or "").strip() or "-"
        bib = (request.form.get("bib") or "").strip() or "-"

        # 코스는 셀렉트에서만 오도록 제한
        allowed_courses = {"3.22km", "6.50km"}
        course = (request.form.get("course") or "3.22km").strip()
        if course not in allowed_courses:
            course = "3.22km"

        # 날짜는 고정
        date = "2025.10.18"

        base = Image.open(BASE_IMG_PATH).convert("RGBA")
        draw = ImageDraw.Draw(base)
        boxes = detect_boxes(base)  # [이름, 배번, 코스, 날짜] 순서에 맞춰 배치

        for text, box in zip([name, bib, course, date], boxes):
            font, pos = fit_text_in_box(draw, text, box)
            sx, sy = pos
            draw.text((sx+1, sy+1), text, font=font, fill=(0,0,0,90))
            draw.text(pos, text, font=font, fill=(28,41,56,255))

        buf = BytesIO()
        base.save(buf, format="PNG")
        buf.seek(0)
        filename = f"o2run_cert_{(bib or 'preview').replace(' ', '_')}.png"
        return send_file(buf, mimetype="image/png", as_attachment=True, download_name=filename)
    except Exception as e:
        return (f"Generation error: {type(e).__name__}: {e}", 500)
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@app.route("/qr")
def qr():
    link = (request.args.get("link") or "").strip()
    if not link:
        ip = get_local_ip()
        port = int(os.environ.get("PORT", "5000"))
        link = f"http://{ip}:{port}/"
    img = qrcode.make(link)
    out = BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return send_file(out, mimetype="image/png")

@app.route("/healthz")
def healthz():
    return "ok"

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
