"""One-off: register the nextore.trial+* Gmail accounts via the real signup flow.

Each account is registered through flows.flow_signup.signup(), which fills the
signup form and pulls the email verification code straight from IMAP (Gmail).

Naming rule (per request):
  First Name = NextoreTrial
  Last Name  = the text between '+' and '@', first letter capitalised
  Password   = Zxc@2026

Run from the repo root:
    .venv/bin/python scripts/register_trial_accounts.py
Use `-s` style headed run automatically (conftest's page fixture is not used here;
we drive Playwright directly so the browser stays visible).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from playwright.sync_api import sync_playwright

from flows.flow_signup import signup

ACCOUNTS = [
    "nextore.trial+sender@gmail.com",
    "nextore.trial+reviewee@gmail.com",
    "nextore.trial+001@gmail.com",
    "nextore.trial+002@gmail.com",
    "nextore.trial+003@gmail.com",
    "nextore.trial+supervisor001@gmail.com",
    "nextore.trial+supervisor002@gmail.com",
    "nextore.trial+supervisor003@gmail.com",
]

FIRST_NAME = "NextoreTrial"
PASSWORD = "Zxc@2026"


def last_name_for(email: str) -> str:
    """Text between '+' and '@', first letter capitalised (e.g. supervisor001 ->
    Supervisor001, 001 -> 001)."""
    local = email.split("@", 1)[0]
    plus = local.split("+", 1)[1] if "+" in local else local
    return plus[:1].upper() + plus[1:]


def main() -> int:
    results = []
    with sync_playwright() as p:
        slow_mo = int(os.getenv("SLOW_MO", "300"))
        browser = p.chromium.launch(headless=False, slow_mo=slow_mo)
        for email in ACCOUNTS:
            last = last_name_for(email)
            print(f"\n=== Registering {email}  ({FIRST_NAME} {last}) ===")
            context = browser.new_context()
            page = context.new_page()
            try:
                signup(
                    page,
                    email=email,
                    first_name=FIRST_NAME,
                    last_name=last,
                    password=PASSWORD,
                )
                results.append((email, last, "OK"))
                print(f"[OK] {email}")
            except Exception as exc:
                results.append((email, last, f"FAIL: {type(exc).__name__}: {exc}"))
                print(f"[FAIL] {email}: {exc}")
            finally:
                context.close()
        browser.close()

    print("\n================ SUMMARY ================")
    ok = 0
    for email, last, status in results:
        print(f"  {status.split(':')[0]:4}  {email:40}  {FIRST_NAME} {last}")
        if status == "OK":
            ok += 1
    print(f"---- {ok}/{len(results)} registered ----")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
