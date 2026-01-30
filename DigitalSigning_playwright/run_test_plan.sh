#!/usr/bin/env bash
set -euo pipefail

# Comment out any line you don't want to run.
CONTINUE_ON_FAIL="${CONTINUE_ON_FAIL:-1}"
if [[ "$CONTINUE_ON_FAIL" == "1" ]]; then
  set +e
else
  set -e
fi

PASS_COUNT=0
FAIL_COUNT=0
FAILED_TESTS=()

run_test() {
  local label="$1"
  local cmd="$2"
  eval "$cmd"
  local status=$?
  if [[ $status -eq 0 ]]; then
    echo "${label}: SUCCESS"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "${label}: FAIL"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    FAILED_TESTS+=("$label")
  fi
  read -r -p "Press Enter to continue to next test..." _
  return $status
}

# Account
run_test "test_account_signup" "pytest -s tests/test_account_signup.py"
run_test "test_account_login_validation" "pytest -s tests/test_account_login_validation.py"
run_test "test_account_forgot_password" "pytest -s tests/test_account_forgot_password.py"

# Setup
run_test "test_add_recipient" "pytest -s tests/test_add_recipient.py"
run_test "test_add_template_validation" "pytest -s tests/test_add_template_validation.py"
run_test "test_add_draft_validation" "pytest -s tests/test_add_draft_validation.py"
run_test "test_my_signature" "pytest -s tests/test_my_signature.py"

# Signing
## Note: parametrize cases in these tests already cover multiple scenarios.
## Example (single case):
##   pytest -s tests/test_sign_sequence.py -k "sender_position=first"
run_test "test_sign_sequence" "pytest -s tests/test_sign_sequence.py"
run_test "test_sign_sequence_without_account" "pytest -s tests/test_sign_sequence_without_account.py"
run_test "test_sign_parallel" "pytest -s tests/test_sign_parallel.py"
run_test "test_sign_parallel_without_account" "pytest -s tests/test_sign_parallel_without_account.py"
run_test "test_use_template_sent_signing_request" "pytest -s tests/test_use_template_sent_signing_request.py"
run_test "test_use_draft_sent_signing_request" "pytest -s tests/test_use_draft_sent_signing_request.py"

# Review
run_test "test_review_approval" "pytest -s tests/test_review_approval.py"
run_test "test_review_reject" "pytest -s tests/test_review_reject.py"

# Filters
run_test "test_filtering_pages" "pytest -s tests/test_filtering_pages.py"
run_test "test_global_search" "pytest -s tests/test_global_search.py"

echo "================ Summary ================"
echo "Passed: ${PASS_COUNT}"
echo "Failed: ${FAIL_COUNT}"
if (( ${#FAILED_TESTS[@]} > 0 )); then
  echo "Failed tests:"
  for t in "${FAILED_TESTS[@]}"; do
    echo " - ${t}"
  done
fi
