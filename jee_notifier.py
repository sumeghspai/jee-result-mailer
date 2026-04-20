"""
JEE Main Session 2 Answer Key Notifier
=======================================
Monitors the NTA JEE Main website and sends an email alert
as soon as the Session 2 answer key is published.

Triggers when this XPath element is found on the page:
  //a[contains(text(),'Provisional') and contains(text(),'April')]

Setup:
  1. Install dependencies:     pip install requests lxml
  2. Run:  python jee_notifier.py
"""

import requests
import smtplib
import time
import random
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from lxml import html as lxml_html

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
CONFIG = {
    # URL to monitor
    "url": "https://jeemain.nta.nic.in/",

    # XPath — alert fires when this element appears on the page
    "xpath": "//a[contains(text(),'Result') and contains(text(),'Session-II')]",
    "xpath_alt": "//a[contains(text(),'Session-II') and not(contains(text(),'Answer') or contains(text(),'Advance') or contains(text(),'Download'))]",
"xpath_alt2": "//a[contains(text(),'Session- II') and not(contains(text(),'Press') or contains(text(),'Advance') )]",
"xpath_alt3": "//a[contains(text(),'Session II') and not(contains(text(),'Answer') or contains(text(),'Advance') or contains(text(),'Download'))]",
"xpath_alt4": "//a[contains(text(),'Session 2') and not(contains(text(),'Conducted') or contains(text(),'Advisory') or contains(text(),'Answer') or contains(text(),'Advance') or contains(text(),'Correction') or contains(text(),'Invit'))]",
    # Random sleep range (in seconds) between each check
    # Script will wait a random time between min and max
    "check_interval_min": 100,
    "check_interval_max": 120,

    # ── Email settings ──
    "sender_email":    "sumeghspai@gmail.com",
    "sender_password": "siid booi hvol ekbm",
    "receiver_emails": [
        "sumeghspai@gmail.com",
        "meghanasureshbabu@gmail.com",
        # "rgsbabu@gmail.com",
        "sumeghspai@zohomail.in"
    ],
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
}
# ─────────────────────────────────────────────

# Logging setup — logs to console and to jee_notifier.log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("jee_notifier.log"),
    ],
)
log = logging.getLogger(__name__)


def fetch_page(url: str) -> str | None:
    """Fetch the page and return its HTML content, or None on failure."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        log.warning(f"Failed to fetch page: {e}")
        return None


def xpath_found(page_html: str, xpath: str) -> tuple[bool, str]:
    """
    Parse the HTML and evaluate the XPath.
    Returns (True, matched_link_text) if any element is found, else (False, "").
    """
    try:
        tree = lxml_html.fromstring(page_html)
        matches = tree.xpath(xpath)
        matches_alt = tree.xpath(CONFIG["xpath_alt"])
        matches_alt2 = tree.xpath(CONFIG["xpath_alt2"])
        matches_alt3 = tree.xpath(CONFIG["xpath_alt3"])
        matches_alt4 = tree.xpath(CONFIG["xpath_alt4"])
        if matches_alt:
            link_text = (matches_alt[0].text_content() or "").strip()
            return True, link_text
        if matches_alt2:
            link_text = (matches_alt2[0].text_content() or "").strip()
            return True, link_text
        if matches_alt3:
            link_text = (matches_alt3[0].text_content() or "").strip()
            return True, link_text
        if matches_alt4:
            link_text = (matches_alt4[0].text_content() or "").strip()
            return True, link_text
        if matches:
            link_text = (matches[0].text_content() or "").strip()
            return True, link_text
        return False, ""
    except Exception as e:
        log.warning(f"XPath evaluation error: {e}")
        return False, ""


def send_email(subject: str, body: str, link_text: str) -> bool:
    """Send an alert email to all recipients. Returns True if at least one succeeds."""
    recipients = CONFIG["receiver_emails"]

    html_body = f"""
    <html><body>
      <h2 style="color:#d62728;">JEE Main Answer Key Alert</h2>
      <p>{body}</p>
      <p><strong>Matched link:</strong> <em>Provisional Answer Key - April</em></p>
      <p>
        <a href="{CONFIG['url']}" style="background:#1f77b4;color:#fff;padding:10px 18px;
           text-decoration:none;border-radius:5px;">Open NTA Website</a>
      </p>
      <hr/>
      <small>Sent by JEE Notifier at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
    </body></html>
    """

    any_success = False
    try:
        with smtplib.SMTP(CONFIG["smtp_host"], CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(CONFIG["sender_email"], CONFIG["sender_password"])

            for recipient in recipients:
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = subject
                    msg["From"]    = CONFIG["sender_email"]
                    msg["To"]      = recipient
                    msg.attach(MIMEText(body, "plain"))
                    msg.attach(MIMEText(html_body, "html"))

                    server.sendmail(CONFIG["sender_email"], recipient, msg.as_string())
                    log.info(f"Alert sent to {recipient}")
                    any_success = True
                except smtplib.SMTPException as e:
                    log.error(f"Failed to send to {recipient}: {e}")

    except smtplib.SMTPException as e:
        log.error(f"SMTP connection error: {e}")

    return any_success


def run():
    log.info("=" * 55)
    log.info("  JEE Main Session 2 Answer Key Notifier - STARTED")
    log.info(f"  Monitoring : {CONFIG['url']}")
    log.info(f"  XPath      : {CONFIG['xpath']}")
    log.info(f"  Interval   : {CONFIG['check_interval_min']}s - {CONFIG['check_interval_max']}s (random)")
    log.info("=" * 55)

    check_count = 0
    alert_sent  = False
    start_time = datetime.now()

    while not alert_sent:
        check_count += 1
        log.info(f"Check #{check_count} - fetching page...")

        page_html = fetch_page(CONFIG["url"])

        if page_html is None:
            log.warning("Skipping this check due to fetch error. Will retry.")
        else:
            found, link_text = xpath_found(page_html, CONFIG["xpath"])
            if found:
                log.info(f"XPath matched! Element text: '{link_text}'")
                subject = "JEE Main Session 2 Answer Key is LIVE!"
                body = (
                    f"The provisional answer key has appeared on the NTA website.\n\n"
                    f"Matched link: \"{link_text}\"\n"
                    f"URL: {CONFIG['url']}\n\n"
                    f"Go check it now!"
                )
                if send_email(subject, body, link_text):
                    alert_sent = True
                    log.info("Monitoring stopped after successful alert.")
                else:
                    log.warning("Email failed. Will keep checking and retry on next match.")
            else:
                log.info("XPath element not found yet. Waiting for next check...")

        if not alert_sent:
            wait = random.randint(CONFIG["check_interval_min"], CONFIG["check_interval_max"])
            log.info(f"Next check in {wait}s...")
            # At the top of run(), before the while loop


# Then inside the loop, after the check
            elapsed = datetime.now() - start_time
            log.info(f"Elapsed time: {str(elapsed).split('.')[0]}")  # trims microseconds
            time.sleep(wait)


if __name__ == "__main__":
    run()