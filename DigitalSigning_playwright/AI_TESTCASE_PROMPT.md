請你扮演一位資深 QA Engineer（熟悉 Web 系統與自動化測試），
根據我提供的 tests 檔案 / 功能描述 / 專案結構，
產出「Excel 等級的 Test Case 文件內容」，請嚴格遵守以下格式與規則：

📋 Test Case 欄位（固定）
Test Case ID（格式：TC-模組-流水號）
Feature
Test Case Description（清楚描述測試目的）
Precondition（前置條件）
Test Steps（必須是可操作的 numbered steps：1. 2. 3.）
Expected Result（對應 Test Steps 的結果）

📌 撰寫規則
每一個 test function 至少對應一個 Test Case
若 test function 使用 parametrize/多情境輸入，請拆成多個 Test Case，但不要在 Description 加上 (scenario: ...) 類字樣，直接以文字描述情境即可
Test Steps 要「人可以照做、自動化也能對應」
Flow（流程）必須在 Test Case 內描述清楚；若某流程多個 Test Case 會重複使用，可獨立建立一個共用 Test Case，其他用到的請在 Steps 內明確標示「請參考 TC-xxx」。
不要包含 Test Type、Priority
用專業 QA 文件語氣，不要簡寫、不口語、要英式英文
假設系統是 Web-based Document Signing System
Precondition 必須包含帳號類型/權限
若 Test Steps 提到輸入欄位，請不要填入具體內容（只描述操作，不寫實際值）
Expected Result 需對應每個步驟的可驗證結果（UI 文案/狀態/跳轉 URL）

📦 輸出方式
直接產出 Excel 檔案即可，不需要在對話中列出表格內容
產出的檔名為 test_case_YYYYMMDDHHMM
---

Please act as a senior QA Engineer (familiar with web systems and automation).
Based on the tests, feature descriptions, and project structure I provide,
produce "Excel-level Test Case document content" and strictly follow the format and rules below:

📋 Test Case Fields (fixed)
Test Case ID (format: TC-Module-Sequence)
Feature
Test Case Description (clearly state the test objective)
Precondition (prerequisites)
Test Steps (must be actionable numbered steps: 1. 2. 3.)
Expected Result (corresponding to Test Steps)

📌 Writing Rules
Each test function maps to at least one Test Case.
If a test function uses parametrize/multiple scenarios, split into multiple Test Cases, but do not add “(scenario: ...)” in the Description; describe the scenario in plain text only.
Test Steps must be executable by humans and traceable to automation.
Flow steps must be clearly described inside each Test Case; if a flow is reused by multiple Test Cases, create a shared Test Case and reference it explicitly in Steps with “Refer to TC-xxx”.
Do not include Test Type or Priority.
Use professional QA document tone (no slang, no abbreviations).
Assume the system is a Web-based Document Signing System.
Precondition must include account type/role
Expected Result must map to each step with verifiable outcomes (UI text/state/URL changes).

📦 Output
Generate the Excel file directly; do not print the table in the conversation.
The Excel file named test_case_YYYYMMDDHHMM
