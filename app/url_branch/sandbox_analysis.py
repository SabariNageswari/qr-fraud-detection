from playwright.sync_api import sync_playwright
import time


def run_sandbox_analysis(url: str, timeout_ms: int = 8000) -> dict:
    """
    Opens the URL in an isolated headless browser to observe real
    behavior — redirects, auto-downloads, popups, suspicious scripts —
    before the actual user ever visits it.

    Returns:
        dict: {
            "final_url": str,
            "redirected": bool,
            "redirect_count": int,
            "triggered_download": bool,
            "popup_count": int,
            "suspicious_scripts": bool,
            "load_error": str or None
        }
    """
    result = {
        "final_url": url,
        "redirected": False,
        "redirect_count": 0,
        "triggered_download": False,
        "popup_count": 0,
        "suspicious_scripts": False,
        "load_error": None
    }

    downloads_triggered = []
    popups_seen = []
    navigation_history = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            # Track navigations (to detect redirects)
            page.on("framenavigated", lambda frame: navigation_history.append(frame.url))

            # Track popups
            page.on("popup", lambda popup: popups_seen.append(popup.url))

            # Track downloads (auto-download = major red flag)
            page.on("download", lambda download: downloads_triggered.append(download.suggested_filename))

            try:
                page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)  # let scripts/redirects settle
            except Exception as nav_error:
                result["load_error"] = f"Navigation error: {nav_error}"

            result["final_url"] = page.url
            result["redirected"] = page.url != url
            result["redirect_count"] = max(0, len(set(navigation_history)) - 1)
            result["triggered_download"] = len(downloads_triggered) > 0
            result["popup_count"] = len(popups_seen)

            # Basic heuristic: check for common suspicious patterns in page scripts
            try:
                page_content = page.content()
                suspicious_keywords = ["eval(", "document.write(unescape", "fromCharCode", "auto-download"]
                result["suspicious_scripts"] = any(k in page_content for k in suspicious_keywords)
            except Exception:
                pass

            browser.close()

    except Exception as e:
        result["load_error"] = f"Sandbox error: {e}"

    return result

