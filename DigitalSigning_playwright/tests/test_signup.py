from datetime import datetime

from flows.flow_signup import signup
from flows.flow_login import login


def test_signup(page) -> None:
    email = f"zihsyuan0603+{datetime.now().strftime('%Y%m%d%H%M%S')}@gmail.com"
    signup(page, email=email)
    login(page, email=email)
