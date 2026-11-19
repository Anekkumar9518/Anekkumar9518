"""Checks that the six live sites answer, and how fast.

Writes data/status.json, which build_svgs.py turns into the terminal in
the editor card. Runs daily on GitHub Actions (.github/workflows/status.yml).
A site only counts as down after three failed tries, so one slow
response doesn't flag it.

Run:  python tools/check_sites.py
"""
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "status.json"
SITES = [
    "https://shubharambhinfraadvisors.com/",
    "https://www.matrixacres.in/",
    "https://visionwavetechnology.com/",
    "https://lmcstore.in/",
    "https://harisabziwala.com/",
    "https://ezzycommerce.store/",
]
UA = "Mozilla/5.0 (compatible; anekkumar-status/1.0; +https://github.com/Anekkumar9518)"


def check(url):
    """One GET; returns (status code or None, milliseconds)."""
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20) as r:
            r.read(4096)
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        code = None
    return code, round((time.perf_counter() - start) * 1000)


def main():
    results = []
    for url in SITES:
        for attempt in range(3):
            code, ms = check(url)
            if code is not None and code < 400:
                break
            time.sleep(5)
        host = url.split("//", 1)[1].strip("/").removeprefix("www.")
        results.append({"host": host, "url": url, "code": code, "ms": ms, "up": code is not None and code < 400})
        print(f"{host:32} {code} {ms}ms")
    data = {"checked": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "sites": results}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
