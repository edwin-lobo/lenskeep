# fetch.py
from __future__ import annotations
import asyncio
import os
import random
import time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from playwright.async_api import async_playwright


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://vsco.co/",
    "Upgrade-Insecure-Requests": "1",
    # These ‘Sec-Fetch-*’ headers sometimes help with strict CDNs:
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
}

# scraper/fetch.py
from __future__ import annotations
import asyncio, os, time, random, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://vsco.co/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
}

def _requests_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(BROWSER_HEADERS)
    retries = Retry(
        total=3,
        backoff_factor=0.8,
        status_forcelist=(403, 429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s

def fetch_with_requests(username: str) -> str:
    sess = _requests_session()
    for host in ("vsco.co", "www.vsco.co"):
        url = f"https://{host}/{username}/gallery"
        time.sleep(random.uniform(0.4, 1.2))
        r = sess.get(url, timeout=30)
        if r.status_code == 200 and r.text:
            return r.text
        if r.status_code == 404:
            raise FileNotFoundError(f"VSCO profile not found: {username}")
    raise PermissionError("Blocked by CDN (403/429) on requests path")

# ------------------ Playwright path ------------------

PLAYWRIGHT_TIMEOUT_MS = int(os.getenv("LENSKEEP_PW_TIMEOUT_MS", "60000"))
PW_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
]

async def _pw_http_get(url: str) -> str:
    # Use Playwright's HTTP client (no page render)
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        # still launch browser to reuse its network stack & cookies if needed
        browser = await p.chromium.launch(headless=True, args=PW_ARGS)
        ctx = await browser.new_context(
            user_agent=BROWSER_HEADERS["User-Agent"],
            locale="en-US",
            timezone_id="UTC",
            extra_http_headers={
                "Accept": BROWSER_HEADERS["Accept"],
                "Accept-Language": BROWSER_HEADERS["Accept-Language"],
                "Referer": BROWSER_HEADERS["Referer"],
                "Upgrade-Insecure-Requests": "1",
            },
        )
        resp = await ctx.request.get(url, timeout=PLAYWRIGHT_TIMEOUT_MS)
        if not resp.ok:
            await browser.close()
            raise RuntimeError(f"HTTP {resp.status} on {url}")
        text = await resp.text()
        await browser.close()
        return text

async def _pw_page_get(url: str) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=(os.getenv("LENSKEEP_PW_HEADLESS", "1") != "0"),
            args=PW_ARGS,
        )
        ctx = await browser.new_context(
            user_agent=BROWSER_HEADERS["User-Agent"],
            locale="en-US",
            timezone_id="UTC",
            extra_http_headers={
                "Accept": BROWSER_HEADERS["Accept"],
                "Accept-Language": BROWSER_HEADERS["Accept-Language"],
                "Referer": BROWSER_HEADERS["Referer"],
                "Upgrade-Insecure-Requests": "1",
            },
            viewport={"width": 1366, "height": 900},
        )
        page = await ctx.new_page()
        # Don’t wait for networkidle; just confirm response committed
        await page.goto(url, wait_until="commit", timeout=PLAYWRIGHT_TIMEOUT_MS)
        # small grace period for HTML to settle
        await page.wait_for_timeout(1500)
        html = await page.content()
        await browser.close()
        return html

def fetch_html(username: str, mode: str = "auto") -> str:
    url = f"https://vsco.co/{username}/gallery"
    if mode == "requests":
        return fetch_with_requests(username)
    if mode == "playwright":
        try:
            return asyncio.run(_pw_http_get(url))
        except Exception:
            return asyncio.run(_pw_page_get(url))
    # auto: try requests, fallback to pw HTTP, then pw page
    try:
        return fetch_with_requests(username)
    except Exception:
        try:
            return asyncio.run(_pw_http_get(url))
        except Exception:
            return asyncio.run(_pw_page_get(url))


def _requests_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(BROWSER_HEADERS)
    retries = Retry(
        total=3,
        backoff_factor=0.8,
        status_forcelist=(403, 429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s

def fetch_with_requests(username: str) -> str:
    session = _requests_session()
    for host in ("vsco.co"):
        url = f"https://{host}/{username}/gallery"
        time.sleep(random.uniform(0.4, 1.2))
        r = session.get(url, timeout=25)
        if r.status_code == 200 and r.text:
            return r.text
        if r.status_code == 404:
            raise FileNotFoundError(f"VSCO profile not found: {url}")
    # If we got here, it’s mostly 403/429 or empty:
    raise PermissionError("Blocked by CDN (403/429) on requests path")

# ---------- Playwright fallback ----------
PLAYWRIGHT_TIMEOUT_MS = int(os.getenv("LENSKEEP_PW_TIMEOUT_MS", "60000"))
PW_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
]

async def _fetch_with_playwright(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=(os.getenv("LENSKEEP_PW_HEADLESS", "1") != "0"),
            args=PW_ARGS,
        )
        context = await browser.new_context(
            user_agent=BROWSER_HEADERS["User-Agent"],
            locale="en-US",
            timezone_id="UTC",
            extra_http_headers={
                "Accept": BROWSER_HEADERS["Accept"],
                "Accept-Language": BROWSER_HEADERS["Accept-Language"],
                "Referer": BROWSER_HEADERS["Referer"],
                "Upgrade-Insecure-Requests": "1",
            },
            viewport={"width": 1366, "height": 900},
        )
        page = await context.new_page()

        # 1) Navigate and wait for DOMContentLoaded (not networkidle)
        await page.goto(url, wait_until="domcontentloaded", timeout=PLAYWRIGHT_TIMEOUT_MS)

        # 2) Try to wait for JSON state presence (most robust signal)
        try:
            await page.wait_for_function(
                """() => {
                    // look for JSON blobs we can parse
                    return (
                        window.__PRELOADED_STATE__ ||
                        window.__NEXT_DATA__ ||
                        !!Array.from(document.scripts).find(s => (s.textContent||'').includes('__PRELOADED_STATE__') || (s.textContent||'').includes('__NEXT_DATA__'))
                    );
                }""",
                timeout=20000,
            )
        except Exception:
            # If that fails, give the page a little more time
            await page.wait_for_timeout(3000)

        html = await page.content()
        await browser.close()
        return html


# def fetch_html(username: str, mode: str = "auto") -> str:
#     if mode == "requests":
#         return fetch_with_requests(username)
#     if mode == "playwright":
#         return asyncio.run(_fetch_with_playwright(f"https://vsco.co/{username}/gallery"))
#     try:
#         return fetch_with_requests(username)
#     except PermissionError:
#         return asyncio.run(_fetch_with_playwright(f"https://vsco.co/{username}/gallery"))
