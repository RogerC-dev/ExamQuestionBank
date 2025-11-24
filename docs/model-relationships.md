# ExamQuestionBank 模型關係一覽

以下依應用模組整理 ORM 模型，並列出欄位（含型別／預設）與關聯，方便檢索全站資料流。若無特別說明，`on_delete` 均為 `models.CASCADE`。

## Users
### User (`users.models.User`)
- 欄位：`email (EmailField, unique)`、`is_admin (BooleanField, default=False)`，其餘繼承自 `AbstractUser`。
- 關聯：被幾乎所有 app 作為 FK（subscriptions、attempts、flashcards、discussions、gamification、analytics 等）。

### Subscription
- 欄位：`user`、`tier (CharField, choices)`、`status (CharField, choices)`、`starts_at (DateTime, auto_now_add)`、`expires_at (DateTime)`、`created_at`、`updated_at`。
- 關聯：`payments` 反向指向 `Payment`；`user.subscriptions` 查詢歷史方案。

### Payment
- 欄位：`subscription`、`amount (Decimal)`、`currency (CharField, default='TWD')`、`status (CharField, choices)`、`payment_method`、`transaction_id (CharField, unique, nullable)`、`stripe_payment_intent_id (CharField, nullable)`、`created_at`、`updated_at`。
- 關聯：追溯到 `Subscription → User`，作為課金稽核資料。

## Exams
### Exam
- 欄位：`name`、`description`、`time_limit (IntegerField, nullable)`、`created_at`、`updated_at`。
- 關聯：`exam_questions`（`question_bank.ExamQuestion`）維持題序；被 `MockExam.exam` 參考。

### MockExam
- 欄位：`user`、`exam (nullable)`、`name`、`subject (FK→question_bank.Subject, nullable)`、`question_count (IntegerField, default=20)`、`time_limit (IntegerField, nullable)`、`ai_generated (Boolean, default=True)`、`generated_at`、`created_at`、`updated_at`。
- 關聯：`analytics.MockExamPerformance.mock_exam`；`user.mock_exams` 查詢個人模考。

## Question Bank
### ExamSeries
- 欄位：`name (CharField, unique)`、`code (CharField, unique)`、`created_at`、`updated_at`。
- 關聯：`sessions` 反向到 `ExamSession`。

### ExamSession
- 欄位：`exam_series`、`year (IntegerField)`、`session (CharField, default='第一試')`、`created_at`、`updated_at`。
- 關聯：`question_sets`、`user_progress`、`essay_submissions`；(`exam_series`, `year`, `session`) 唯一。

### QuestionSet
- 欄位：`exam_session`、`subject (nullable)`、`subject_name (CharField, nullable)`、`question_type (CharField, default='選擇題')`、`created_at`、`updated_at`。
- 關聯：聚合同場次題目，可搭配 `Subject` 查詢。

### Tag
- 欄位：`name (unique)`、`category (CharField, default='general')`、`created_at`、`updated_at`。
- 關聯：與 `Question` 透過 `QuestionTag` 中介表建立多對多。

### Question
- 欄位：`subject (CharField)`、`category (CharField)`、`question_type (choices)`、`difficulty (choices)`、`status (draft/published)`、`content (Text)`、`explanation (Text, nullable)`、`created_by (FK→User, nullable)`、`created_at`、`tags (ManyToMany → Tag, through QuestionTag)`。
- 關聯：被 `QuestionOption`、`ExamQuestion`、`Attempt`、`Note`、`Bookmark`、`Flashcard`、`Discussion`、`UserProgress` 等引用；並與 `Tag` 維持多對多標籤。

### QuestionOption
- 欄位：`question`、`content (Text)`、`is_correct (Boolean, default=False)`、`order (IntegerField)`。
- 關聯：`attempts` ManyToMany 透過 `Attempt.selected_options`。

### ExamQuestion
- 欄位：`exam (FK→exams.Exam)`、`question (FK→Question)`、`order (IntegerField)`、`points (Decimal, nullable)`。
- 關聯：連結考卷與題目；`unique_together` 確保單卷題目與順序唯一。

### Attempt
- 欄位：`user`、`question`、`selected_options (ManyToMany → QuestionOption)`、`is_correct (Boolean)`、`created_at`。
- 關聯：提供作答記錄，供 XP、分析與推薦使用。

### Note
- 欄位：`user`、`question`、`content (Text)`、`created_at`、`updated_at`；(`user`, `question`) 唯一。

### Bookmark
- 欄位：`user`、`question`、`created_at`；(`user`, `question`) 唯一。

### AIChatHistory
- 欄位：`user`、`message (Text)`、`response (Text)`、`context_type (CharField, nullable)`、`context_id (Integer, nullable)`、`created_at`。

### Subject
- 欄位：`name (unique)`、`code (unique)`、`category (CharField, default='general')`、`description (Text, nullable)`、`created_at`、`updated_at`。
- 關聯：供 `MockExam`、`QuestionSet`、`UserProgress`、`EssaySubmission`、`StudyRecommendation`、`StudyMetric` 等共用。

### UserProgress
- 欄位：`user`、`question`、`subject (nullable)`、`exam_session (nullable)`、`is_correct (Boolean)`、`time_spent (Integer)`、`attempt_count (Integer)`、`last_attempt_at (DateTime, auto_now)`、`mastery_level (choices)`、`created_at`。

### StudySession
- 欄位：`user`、`started_at (auto_now_add)`、`ended_at (nullable)`、`duration (Integer)`、`questions_attempted (Integer)`、`accuracy (Decimal)`、`subjects_covered (ManyToMany → Subject)`。

### EssaySubmission
- 欄位：`user`、`subject (nullable)`、`exam_year (Integer)`、`exam_session (nullable)`、`question_text (Text)`、`answer_text (Text)`、`status (choices)`、`submitted_at`、`updated_at`。

### EssayGrading
- 欄位：`essay_submission (OneToOne)`、`score (Decimal)`、`max_score (Decimal, default=100)`、`feedback (Text)`、`strengths (Text, nullable)`、`weaknesses (Text, nullable)`、`suggestions (Text, nullable)`、`grading_method (choices)`、`graded_at`。

### StudyRecommendation
- 欄位：`user`、`recommendation_type (choices)`、`subject (nullable)`、`priority (choices)`、`content (Text)`、`generated_at`、`is_read (Boolean)`、`read_at (DateTime, nullable)`。

## Flashcards
### Flashcard
- 欄位：`user`、`question`、`status (choices)`、`ease_factor (Float, default=2.5)`、`interval (Integer)`、`repetition (Integer)`、`next_review_date (DateField, default=timezone.now)`、`last_reviewed_at (DateTime, nullable)`、`review_count (Integer)`、`created_at`；(`user`, `question`) 唯一。
- 關聯：`review_logs` 反向指向 `FlashcardReviewLog`。

### FlashcardReviewLog
- 欄位：`flashcard`、`user`、`rating (Integer, choices 1-5)`、`review_interval (Integer)`、`reviewed_at`。

## Discussions
### Discussion
- 欄位：`question (nullable)`、`user`、`title`、`content (Text)`、`parent (Self FK, nullable)`、`upvotes (Integer)`、`downvotes (Integer)`、`status (choices)`、`is_flagged (Boolean)`、`created_at`、`updated_at`。
- 關聯：自我遞迴 replies；與 `DiscussionVote`、`ContentReport` 互動。

### DiscussionVote
- 欄位：`discussion`、`user`、`vote_type (choices up/down)`、`created_at`；(`discussion`, `user`) 唯一。

### ContentReport
- 欄位：`discussion`、`user`、`reason (CharField)`、`notes (Text, blank=True)`、`created_at`、`resolved_at (DateTime, nullable)`。

## Gamification
### Badge
- 欄位：`name (unique)`、`description (Text)`、`icon (CharField, blank=True)`、`trigger (choices)`、`threshold (Integer)`、`xp_reward (Integer)`、`created_at`。
- 關聯：`awards` 反向至 `UserBadge`。

### UserBadge
- 欄位：`user`、`badge`、`awarded_at`；(`user`, `badge`) 唯一。

### UserXPLog
- 欄位：`user`、`source (choices)`、`delta (Integer)`、`metadata (JSON, nullable)`、`created_at`。

### StudyGroup
- 欄位：`name`、`description (Text, blank=True)`、`owner`、`visibility (choices)`、`max_members (Integer)`、`created_at`、`updated_at`。
- 關聯：`memberships` 維護成員。

### StudyGroupMembership
- 欄位：`group`、`user`、`role (choices member/moderator)`、`joined_at`；(`group`, `user`) 唯一。

### NotificationSchedule
- 欄位：`user`、`title`、`payload (JSON)`、`scheduled_for (DateTime)`、`channel (choices)`、`sent_at (DateTime, nullable)`、`created_at`。

## Analytics
### StudyMetric
- 欄位：`user`、`subject (nullable)`、`accuracy (Decimal)`、`total_attempts (Integer)`、`correct_attempts (Integer)`、`average_time (Integer)`、`updated_at`；(`user`, `subject`) 唯一。

### Recommendation
- 欄位：`user`、`title`、`detail (Text)`、`created_at`、`seen (Boolean)`。

### MockExamPerformance
- 欄位：`user`、`mock_exam (FK→exams.MockExam)`、`score (Decimal)`、`duration_seconds (Integer)`、`completed_at`。

## 跨模組資料流
1. **使用者中心化**：所有互動／付費／遊戲化資料均以 `User` 為主鍵，`on_delete=CASCADE` 代表刪除使用者會清掉相關記錄。
2. **題庫共享**：`Question` 連動考卷 (`ExamQuestion`)、練習 (`Attempt`)、複習 (`Flashcard`) 與社群 (`Discussion`)，成為學習內容的樞紐。
3. **考試串接**：`Exam` 與 `ExamQuestion` 建立正式考卷；`MockExam` 搭配 `Subject` 與 `MockExamPerformance` 產生模考追蹤。
4. **追蹤→分析**：`Attempt`、`UserProgress`、`StudySession`、`FlashcardReviewLog` 等資料餵入 `StudyMetric`、`StudyRecommendation`，用於演算法建議。
5. **社群／遊戲化結合**：`Discussion`、`StudyGroup`、`Badge`、`UserXPLog` 等與題庫、使用者資料互相串聯，再透過 `NotificationSchedule` 推播提醒。

> 如需 ERD，可直接以此欄位/關聯列表繪製 Mermaid 或其他圖形工具。


