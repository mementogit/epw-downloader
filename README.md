# EPW Downloader (Unofficial)

A small Python script that downloads full weekly issues of the
**Economic & Political Weekly (EPW)** as PDFs, using **your own paid EPW
subscription**.

It saves each issue as one PDF (the same full-magazine file EPW's online
viewer shows), e.g. `EPW_2026-04-04_Issue14.pdf`, and skips issues you
already have, so you can rerun it every week to get the new one.

> **Not affiliated with or endorsed by Economic and Political Weekly.**
> This script does not bypass any paywall. It only downloads what your own
> logged-in subscription already lets you download.

## Disclaimer: made with AI

I am not a programmer. This script was written with the help of an AI
assistant (Claude, by Anthropic), and I have tested it only for my own use.
It may contain bugs, and it will likely stop working if EPW changes its
website. Use it at your own risk, and please read the code before running it.

## Requirements

- Python 3.9 or newer ([python.org](https://www.python.org/downloads/))
- An active EPW subscription that includes online access
- The `requests` package:

```
pip install requests
```

## Setup

1. Download `epw_download.py` into a folder of your choice. PDFs are saved
   in whichever folder you run the script from.
2. Log in to [epw.in](https://www.epw.in) in your normal browser. Check that
   an issue opens in the magazine viewer.
3. Export your cookies for **www.epw.in** to a file named `cookies.txt` in
   the same folder, for example with the browser extension
   "Get cookies.txt LOCALLY".

**Keep `cookies.txt` private.** It is your logged-in session. Never upload
or share it. If the script later says you are not logged in, log in again
and re-export it.

## Usage

```
python epw_download.py                                     # 4 Apr 2026 to today
python epw_download.py --from 2026-06-01                   # from a date to today
python epw_download.py --from 2026-04-04 --to 2026-04-04   # a single issue
```

Issues are numbered by week (the first Saturday of the year is Issue 1), and
the script works out issue numbers from the dates. It waits a couple of
seconds between requests to stay gentle on EPW's servers.

## Please use responsibly

EPW's Terms and Conditions allow downloading for **your own personal,
non-commercial use** only. So:

- Do **not** share, re-upload or distribute the downloaded PDFs.
- Do **not** share your login or `cookies.txt`.
- Do **not** use it to overload EPW's website.

EPW is an independent, reader-supported publication. If you find it
valuable, please keep subscribing.

## License

The code is released under the [MIT License](LICENSE). This covers **only
the script**, not any EPW content: all magazine content remains the
copyright of Economic and Political Weekly.
