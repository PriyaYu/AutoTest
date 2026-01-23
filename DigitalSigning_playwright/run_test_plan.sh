#!/usr/bin/env bash
set -euo pipefail

# Comment out any line you don't want to run.
pytest tests/test_login_validation.py
pytest tests/test_review_approval.py
pytest tests/test_review_reject.py
pytest tests/test_sign_parallel.py
pytest tests/test_sign_sequence.py
