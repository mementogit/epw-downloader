#!/usr/bin/env python3
"""
Unofficial EPW (Economic & Political Weekly) full-issue downloader.

NOT affiliated with or endorsed by Economic and Political Weekly.
Requires YOUR OWN paid EPW subscription; it only downloads what your login
already allows and does not bypass any paywall. Per EPW's Terms and
Conditions, downloaded issues are for your own personal, non-commercial use:
do not share, re-upload or distribute the PDFs, and never share cookies.txt
(it is your login).

Downloads the complete printed magazine (the same PDF EPW's page viewer shows)
for every weekly issue from a start date up to the latest, into the folder you
run the script from:

    EPW_2026-04-18_Issue16.pdf
    EPW_2026-04-25_Issue17.pdf
    ...

Issues you already have are skipped, so just run it again each week.

LOGIN: log in to epw.in in your normal browser, then export your cookies to
"cookies.txt" in this folder (extension "Get cookies.txt LOCALLY", while on
www.epw.in). Re-export it if the script ever says you're not logged in.
Keep cookies.txt private - it is your logged-in session.

INSTALL:  pip install requests
USAGE:    python epw_download.py                    # 4 Apr 2026 -> today
          python epw_download.py --from 2026-06-01  # from 1 Jun 2026
          python epw_download.py --from 2026-04-04 --to 2026-04-04  # one issue
"""

import argparse
import datetime as dt
import http.cookiejar
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, urljoin

import requests

BASE = "https://www.epw.in"
DEFAULT_START = "2026-04-04"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
HERE = Path.cwd()


# ------------------------------------------------------------------ login
def make_session(browser=None):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": BASE + "/"})
    txt = HERE / "cookies.txt"
    if browser:
        try:
            import browser_cookie3
        except ImportError:
            sys.exit("--browser needs:  pip install browser-cookie3")
        s.cookies.update(getattr(browser_cookie3, browser)(domain_name="epw.in"))
        print(f"Using login from {browser}")
    elif txt.exists():
        jar = http.cookiejar.MozillaCookieJar(str(txt))
        jar.load(ignore_discard=True, ignore_expires=True)
        s.cookies.update(jar)
        print("Using cookies.txt")
    else:
        sys.exit("cookies.txt not found in this folder.\n"
                 "Log in to epw.in in your browser, export cookies.txt "
                 "(extension 'Get cookies.txt LOCALLY') into:\n  " + str(HERE))
    return s


# ------------------------------------------------------------------ dates
def first_saturday(year):
    jan1 = dt.date(year, 1, 1)
    return jan1 + dt.timedelta((5 - jan1.weekday()) % 7)


def issue_for(saturday):
    """Issue 1 = first Saturday of the year, then one per week."""
    return (saturday - first_saturday(saturday.year)).days // 7 + 1


def saturdays(start, end):
    d = start + dt.timedelta((5 - start.weekday()) % 7)
    while d <= end:
        yield d
        d += dt.timedelta(7)


def roman(n):
    out = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
                 (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
                 (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += s
            n -= v
    return out


# ------------------------------------------------------------------ finding the PDF
def pdf_from_issue_page(session, year, label):
    """Look for the full-issue PDF link in the issue page's HTML."""
    try:
        r = session.get(f"{BASE}/journal/{year}/{label}", timeout=60)
    except requests.RequestException:
        return None, False
    if r.status_code != 200:
        return None, False
    html = r.text.replace("\\/", "/")
    m = re.search(rf"""[^"'\s>]*/system/files/pdf/{year}_\d+/{re.escape(label)}/"""
                  r"""EPW_Vol[^"'<>]*?\.pdf""", html, re.I)
    return (urljoin(BASE, m.group(0)) if m else None), True


def guessed_urls(year, label, sat):
    """Build the link from EPW's naming pattern, e.g.
    /system/files/pdf/2026_61/14/EPW_Vol LXI_No 14_4 April 2026.pdf"""
    vol = year - 1965
    folder = f"{BASE}/system/files/pdf/{year}_{vol}/{label}/"
    dates = [sat]
    if "-" in label:                      # double issue: try either week's date
        dates.append(sat + dt.timedelta(7))
    for d in dates:
        for month in (d.strftime("%B"), d.strftime("%b")):
            name = f"EPW_Vol {roman(vol)}_No {label}_{d.day} {month} {d.year}.pdf"
            yield folder + quote(name)


def fetch_pdf(session, url, referer):
    try:
        r = session.get(url, timeout=300, headers={"Referer": referer})
    except requests.RequestException as e:
        print(f"    ! {e}")
        return None
    if r.status_code == 200 and r.content[:5] == b"%PDF-":
        return r.content
    if r.status_code in (401, 403) or (r.status_code == 200 and b"<html" in r.content[:2000].lower()):
        return "LOGIN"
    return None


# ------------------------------------------------------------------ main
def already_have(year, n):
    for p in HERE.glob(f"EPW_{year}-*_Issue*.pdf"):
        if str(n) in p.stem.split("_Issue")[-1].split("-"):
            return True
    return False


def download_issue(session, year, n, sat, delay):
    for label in (str(n), f"{n}-{n + 1}"):              # normal or double issue
        page_url = f"{BASE}/journal/{year}/{label}"
        link, page_exists = pdf_from_issue_page(session, year, label)
        if not page_exists:
            continue
        candidates = [link] if link else []
        candidates += [u for u in guessed_urls(year, label, sat) if u not in candidates]
        login_problem = False
        for url in candidates:
            data = fetch_pdf(session, url, page_url)
            time.sleep(delay)
            if data == "LOGIN":
                login_problem = True
                continue
            if data:
                out = HERE / f"EPW_{sat}_Issue{label}.pdf"
                out.write_bytes(data)
                print(f"  saved {out.name}  ({len(data) / 1e6:.1f} MB)")
                return [n, n + 1] if "-" in label else [n]
        if login_problem:
            sys.exit("\nEPW refused the PDF - you're not logged in.\n"
                     "Log in to epw.in in your browser, re-export cookies.txt, and rerun.")
        print(f"  ! Issue {label} page exists but its PDF wasn't found.\n"
              f"    Open {page_url}, find the PDF link (F12 > Network > 'pdf') and send it to me.")
        return [n, n + 1] if "-" in label else [n]
    print(f"  Issue {n} ({sat}) not on the site yet")
    return []


def main():
    ap = argparse.ArgumentParser(description="Download full EPW issues as PDFs")
    ap.add_argument("--from", dest="start", default=DEFAULT_START,
                    help=f"start date YYYY-MM-DD (default {DEFAULT_START})")
    ap.add_argument("--to", dest="end", help="end date YYYY-MM-DD (default today)")
    ap.add_argument("--browser", choices=["firefox", "chrome", "edge", "brave"],
                    help="read login from this browser instead of cookies.txt")
    ap.add_argument("--delay", type=float, default=2.0,
                    help="seconds between requests (default 2)")
    args = ap.parse_args()

    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end) if args.end else dt.date.today()
    session = make_session(args.browser)

    covered = set()
    for sat in saturdays(start, end):
        year, n = sat.year, issue_for(sat)
        if (year, n) in covered:
            continue
        if already_have(year, n):
            print(f"Issue {n} ({sat}) already downloaded")
            covered.add((year, n))
            continue
        print(f"Issue {n} ({sat})")
        covered.update((year, x) for x in download_issue(session, year, n, sat, args.delay))

    print("\nAll done.")


if __name__ == "__main__":
    main()
