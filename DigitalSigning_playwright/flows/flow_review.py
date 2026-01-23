def review_action(page, action="reject"):
    page.get_by_text("Review").click()
    page.get_by_role("button", name="Review").first.click()
    action_lower = action.lower()
    if action_lower == "approve":
        page.get_by_role("button", name="Approve").click()
    elif action_lower == "reject":
        page.get_by_role("button", name="Reject").click()
    else:
        raise ValueError("action must be 'approve' or 'reject'")
    return page
