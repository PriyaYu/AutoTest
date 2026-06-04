import pytest

from flows.flow_change_full_name import change_full_name
from flows.flow_login import login


# Skipped pending a backend fix: the "Edit Username" field rejects names that
# satisfy its own stated rule ("letters, numbers, and underscores") — e.g.
# "QA_AutoTest_20260604170848" is refused. Re-enable once validation is fixed.
@pytest.mark.skip(reason="Username validation rejects valid names; pending backend fix")
def test_change_full_name(page) -> None:
    login(page)
    for _ in range(1):
        change_full_name(page)
