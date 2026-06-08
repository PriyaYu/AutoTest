import pytest

from flows.flow_login import login
from flows.flow_logout import logout


@pytest.mark.parametrize("entry", ["menu", "dropdown"])
def test_logout(page, entry) -> None:
    login(page)
    logout(page, entry)
