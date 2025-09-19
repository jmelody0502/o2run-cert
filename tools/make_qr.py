import sys
import qrcode

def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/make_qr.py <URL> <out.png>")
        sys.exit(1)
    url, out = sys.argv[1], sys.argv[2]
    img = qrcode.make(url)
    img.save(out)
    print("Saved", out)

if __name__ == "__main__":
    main()
