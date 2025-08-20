import os, csv, time
import requests
from urllib.parse import quote

BASE = "http://127.0.0.1:8000"
OUT_DIR = "datasets"
os.makedirs(os.path.join(OUT_DIR, "clean"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "polluted"), exist_ok=True)

def save_html(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def fetch(url):
    return requests.get(url, timeout=5)

def main():
    with open("payloads.txt", "r", encoding="utf-8") as f:
        payloads = [line.strip() for line in f if line.strip()]
    rows = []
    ts = int(time.time())

    for i, p in enumerate(payloads, 1):
        # polluted (未修復)
        u = f"{BASE}/data.php?tpl={quote(p)}&token=demo&200=val"
        r = fetch(u)
        fname = f"polluted_reflected_{ts}_{i}.html"
        save_html(os.path.join(OUT_DIR, "polluted", fname), r.text)
        rows.append([fname, "polluted", "reflected", p, u])

        # clean (已修復)
        u = f"{BASE}/data_safe.php?tpl={quote(p)}&token=demo&200=val"
        r = fetch(u)
        fname = f"clean_reflected_{ts}_{i}.html"
        save_html(os.path.join(OUT_DIR, "clean", fname), r.text)
        rows.append([fname, "clean", "reflected", p, u])

    with open(os.path.join(OUT_DIR, "labels.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["filename","label","xss_type","payload","source_url"])
        w.writerows(rows)

    print(f"OK, wrote {len(rows)} samples. Save under {OUT_DIR}/")

if __name__ == "__main__":
    main()
