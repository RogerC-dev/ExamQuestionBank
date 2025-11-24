# API 接口總覽

- Base URL: `/api/v1/`
- Auth: JWT（`/api/v1/auth/login/` 取得 access/refresh、`/api/v1/auth/refresh/` 換發）
- 所有業務端點預設都需 `IsAuthenticated`，除非另有註明。

## 目錄
1. [認證與帳號](#認證與帳號)
2. [訂閱與付款](#訂閱與付款)
3. [題庫 Question Bank](#題庫-question-bank)
4. [考卷與模擬測驗](#考卷與模擬測驗)
5. [申論題與學習分析](#申論題與學習分析)
6. [AI / 擴充功能端點](#ai--擴充功能端點)
7. [快閃卡](#快閃卡)
8. [討論區](#討論區)
9. [遊戲化與學習小組](#遊戲化與學習小組)
10. [進階分析（analytics app）](#進階分析analytics-app)

---

## 認證與帳號
| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/api/v1/auth/login/` | POST | 取得 JWT access/refresh token | 任何 | body: `{username, password}`。
| `/api/v1/auth/refresh/` | POST | 使用 refresh 兌換新 access token | 已持有 refresh | body: `{refresh}`。

## 訂閱與付款
來源：`users/subscription_views.py`

| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/api/v1/subscription/status/` | GET | 查詢當前訂閱層級與到期日 | 登入 | 回傳 `tier/status/expires_at/is_active`。
| `/api/v1/subscription/create/` | POST | 建立訂閱並記錄付款 | 登入 | body: `{tier, payment_intent_id}`，目前支援 `premium`。會自動取消舊訂閱並寫入 `Payment`。
| `/api/v1/subscription/cancel/` | POST | 取消有效訂閱 | 登入 | 若無有效訂閱回傳 404。

## 題庫 Question Bank
來源：`question_bank.urls`（同時掛載於 `/api/v1/` 與 `/api/v1/question_bank/`）。以下以 `/api/v1/` 版本為主。

### 題目 CRUD
`QuestionViewSet` （`/questions/`）

| Path | Method | 說明 | 權限 | Serializer/備註 |
| --- | --- | --- | --- | --- |
| `/questions/` | GET | 題目列表（簡化欄位） | 登入 | `QuestionListSerializer`，支援 query filter 於 viewset 中定義（可依後續擴充）。
| `/questions/` | POST | 新增題目（含選項、標籤） | 登入 | `QuestionCreateUpdateSerializer`。
| `/questions/{id}/` | GET | 題目詳情（含 `options/tags`） | 登入 | `QuestionDetailSerializer`。
| `/questions/{id}/` | PUT/PATCH | 更新題目 | 登入 | 需傳相同 serializer。
| `/questions/{id}/` | DELETE | 刪除題目 | 登入 | - |

### PDF 匯入
| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/extract-questions-pdf/` | POST | 上傳考題 PDF，解析題目 JSON | 登入 | multipart `file`。成功回傳題目結構（含 count/level/subject 等）。
| `/extract-answers-pdf/` | POST | 上傳答案 PDF，解析答案 JSON | 登入 | multipart `file`。回傳 `answers` 與備註。

## 考卷與模擬測驗
`exams.urls`

### ExamViewSet `/exams/`
| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/exams/` | GET | 考卷列表 | 登入 | `ExamListSerializer`。
| `/exams/` | POST | 建立考卷 | 登入 | `ExamCreateUpdateSerializer`。
| `/exams/{id}/` | GET | 考卷詳情含題目 | 登入 | `ExamDetailSerializer`。
| `/exams/{id}/` | PUT/PATCH | 更新考卷 | 登入 | - |
| `/exams/{id}/` | DELETE | 刪除考卷 | 登入 | - |
| `/exams/{id}/add_question/` | POST | 加題至考卷 | 登入 | body: `{question, order, points}`。回傳 `ExamQuestionSerializer`。
| `/exams/{id}/remove_question/?exam_question_id=...` | DELETE | 移除題目 | 登入 | 需 query 參數。
| `/exams/{id}/update_question/` | PATCH | 調整題目順序/配分 | 登入 | body: `exam_question_id` + 欲更新欄位。

### Mock Exam
| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/mock-exams/generate/` | POST | 產生模擬測驗 | 登入 | `MockExamGenerateSerializer`，可選擇 AI 生成或題庫抽題。
| `/mock-exams/` | GET | 取得個人模擬測驗列表 | 登入 | `MockExamSerializer`。
| `/mock-exams/{id}/` | GET | 單筆模考詳情 | 登入 | - |
| `/mock-exams/{id}/` | DELETE | 刪除模考 | 登入 | - |

## 申論題與學習分析
### Essay APIs (`question_bank/essay_views.py`)
| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/essays/submit/` | POST | 提交申論題答案並觸發 AI 批改 | 登入 | `EssaySubmissionCreateSerializer`。
| `/essays/` | GET | 取得申論題列表，支援 `subject/status/page` | 登入 | 分頁 20 筆，`EssaySubmissionSerializer`。
| `/essays/{id}/` | GET | 取得單筆申論題詳情 | 登入 | - |
| `/essays/{id}/grading/` | GET | 取得批改結果 | 登入 | 若尚未批改回 404。

### 學習進度/建議（`question_bank/analytics_views.py`）
| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/analytics/progress/` | GET | 整體進度統計，支援 `time_range` | 登入 | 回傳總題數、完成度、30 日趨勢。
| `/analytics/subjects/` | GET | 各科目練習成效 | 登入 | 無參數。
| `/analytics/trends/` | GET | 指定天數趨勢（預設 30） | 登入 | query `days`。
| `/analytics/recommendations/` | GET | 學習建議列表，支援 `is_read/priority` | 登入 | `StudyRecommendationSerializer`。
| `/analytics/recommendations/` | POST | 觸發 AI 生成建議 | 登入 | 無 body，使用內部進度資料。
| `/analytics/recommendations/{id}/read/` | PATCH | 標記建議已讀 | 登入 | 立即寫入 `is_read/read_at`。

## AI / 擴充功能端點
### AI Chat & Case
| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/ai/chat/` | POST | AI 對話，含可選 `context_type/context_id` | 登入 | 受每日 10 次限制（非 premium）。回傳 `response/chat_id`。
| `/ai/history/` | GET | 列出聊天記錄 | 登入 | query `limit/offset`。
| `/ai/analyze-case/` | POST | 案例分析摘要 | 登入 | body: `{case_text}`；沿用每日限制。

### Extension Sync
| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/extension/stats/` | GET | 提供擴充功能用的統計 | 登入 | 回傳書籤數、快閃卡數、練習次數等。
| `/extension/sync-bookmarks/` | POST | 從延伸套件同步書籤 | 登入 | body: `bookmarks[] {question_id, case_url, case_title}`。
| `/extension/sync-flashcards/` | POST | 同步快閃卡進度 | 登入 | body: `flashcards[] {question_id, last_reviewed, next_review, ...}`。

## 快閃卡
`FlashcardViewSet` (`/flashcards/`)

| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/flashcards/` | GET | 列出個人卡片，可用 `status` 或 `due` | 登入 | `status=due` 篩今日需複習。
| `/flashcards/` | POST | 建立快閃卡（綁定題目） | 登入 | `FlashcardSerializer`。
| `/flashcards/{id}/` | DELETE | 刪除 | 登入 | - |
| `/flashcards/due/` | GET | 直接取得今日/逾期待複習卡 | 登入 | 自訂 action。
| `/flashcards/{id}/review/` | POST | 回傳評分並跑 SM-2 | 登入 | body: `{rating:1-5}`。同時新增 `FlashcardReviewLog`。
| `/flashcards/stats/` | GET | 卡片統計（total/due/streak/next_review） | 登入 | - |
| `/flashcards/history/` | GET | 最近 50 筆複習紀錄 | 登入 | 使用 `FlashcardReviewLogSerializer`。

## 討論區
`DiscussionViewSet` (`/discussions/`)

| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/discussions/` | GET | 討論串列表，可用 `?question=` 篩題目 | 登入 | 僅取頂層（parent=null）。
| `/discussions/` | POST | 建立新討論 | 登入 | body: `{title, content, question}`。
| `/discussions/{id}/` | CRUD | 讀取/更新/刪除討論 | 登入 | - |
| `/discussions/{id}/reply/` | POST | 回覆指定討論 | 登入 | body 同上，會自動沿用 `question`。
| `/discussions/{id}/vote/` | POST | 投票 | 登入 | body: `{vote_type: up/down}`，自動更新 `upvotes/downvotes`。
| `/discussions/{id}/report/` | POST | 檢舉 | 登入 | body: `{reason, notes}`。

## 遊戲化與學習小組
`gamification.urls`

| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/gamification/badges/` | GET | 可獲得的徽章列表 | 登入 | read-only。
| `/gamification/user-badges/` | GET | 個人已解鎖徽章 | 登入 | - |
| `/gamification/user-xp/` | GET | XP log 列表 | 登入 | 支援 `/gamification/user-xp/total/` 取得 XP 總和。
| `/study-groups/` | CRUD | 學習小組管理 | 登入 | 建立時自動把建立者設為 moderator。
| `/study-groups/{id}/join/` | POST | 加入小組 | 登入 | 若已存在則回傳現有 membership。
| `/study-groups/{id}/leave/` | POST | 退出小組 | 登入 | - |
| `/notifications/` | CRUD | 提醒排程（Email/Push/In-app） | 登入 | create 時自動綁定 user。

## 進階分析（analytics app）
若需要更細部資料記錄，可透過 `analytics` app 的 ViewSet。

| Path | Method | 說明 | 權限 | 備註 |
| --- | --- | --- | --- | --- |
| `/analytics/metrics/` | CRUD | 直接操作 `StudyMetric`（聚合資料） | 登入 | 一般情境由系統寫入，前端可讀取或上傳自定資料。
| `/analytics/recommendations/` | CRUD | 操作 `analytics.Recommendation`（與 question_bank 的建議不同 table） | 登入 | 主要給資料科或內部分析使用。
| `/analytics/mock-performance/` | CRUD | 模考成績紀錄 | 登入 | `MockExamPerformanceSerializer`，建議於模考繳卷後寫入。

---

### 其他注意事項
- 大多端點使用 `IsAuthenticated`，若需開放匿名需另調整 permission。
- 部分 AI/擴充功能端點對免費用戶有每日次數限制，已於各 view 內處理。
- `QuestionViewSet`、`ExamViewSet` 等預設支援標準 DRF 分頁、搜尋/排序（視 `settings.py` 中的全域設定）。
- 若需要檢視即時 API schema，可至根路徑 `/swagger/` 或 `/redoc/`。

