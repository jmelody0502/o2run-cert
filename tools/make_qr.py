import sys, qrcode
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/make_qr.py <URL> <out.png>")
        raise SystemExit(1)
    img = qrcode.make(sys.argv[1])
    img.save(sys.argv[2])
    print("Saved", sys.argv[2])
