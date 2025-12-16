# ExamQuestionBank API 文件

> 司律考題題庫系統 API 文件
> 
> Base URL: `/api/v1/`

---

## 目錄

1. [認證 (Authentication)](#1-認證-authentication)
2. [使用者 (Users)](#2-使用者-users)
3. [題目 (Questions)](#3-題目-questions)
4. [標籤 (Tags)](#4-標籤-tags)
5. [科目 (Subjects)](#5-科目-subjects)
6. [考卷 (Exams)](#6-考卷-exams)
7. [模擬測驗 (Mock Exams)](#7-模擬測驗-mock-exams)
8. [考試結果 (Exam Results)](#8-考試結果-exam-results)
9. [錯題本 (Wrong Questions)](#9-錯題本-wrong-questions)
10. [收藏 (Bookmarks)](#10-收藏-bookmarks)
11. [快閃卡 (Flashcards)](#11-快閃卡-flashcards)
12. [AI 功能 (AI Features)](#12-ai-功能-ai-features)
13. [申論題 (Essays)](#13-申論題-essays)
14. [討論區 (Discussions)](#14-討論區-discussions)
15. [遊戲化 (Gamification)](#15-遊戲化-gamification)
16. [學習分析 (Analytics)](#16-學習分析-analytics)
17. [訂閱 (Subscription)](#17-訂閱-subscription)
18. [擴充功能 (Extension)](#18-擴充功能-extension)
19. [PDF 解析 (PDF Parser)](#19-pdf-解析-pdf-parser)

---

## 1. 認證 (Authentication)

### 1.1 登入

取得 JWT Token

```
POST /api/v1/auth/login/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| username | string | ✓ | 使用者名稱 |
| password | string | ✓ | 密碼 |

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

Token 包含額外資訊：`username`, `email`, `is_staff`, `is_superuser`

---

### 1.2 註冊

```
POST /api/v1/auth/register/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| username | string | ✓ | 使用者名稱 |
| email | string | ✓ | 電子郵件 |
| password | string | ✓ | 密碼 |
| password_confirm | string | ✓ | 確認密碼 |

**Response (201):**
```json
{
  "message": "註冊成功",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "is_staff": false,
    "is_admin": false,
    "date_joined": "2025-01-01T00:00:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

---

### 1.3 刷新 Token

```
POST /api/v1/auth/refresh/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| refresh | string | ✓ | Refresh Token |

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

---

### 1.4 取得當前使用者

```
GET /api/v1/auth/me/
```

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "is_staff": false,
  "is_admin": false,
  "date_joined": "2025-01-01T00:00:00Z"
}
```

---

## 2. 使用者 (Users)

> 詳見 [認證 (Authentication)](#1-認證-authentication)

---

## 3. 題目 (Questions)

### 3.1 取得題目列表

```
GET /api/v1/questions/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| keyword | string | 搜尋題目內容、科目、分類、選項 |
| tags | string | 標籤 ID（逗號分隔，如 `1,2,3`）|
| tag_mode | string | 標籤模式：`or`（預設）或 `and` |
| page | int | 頁碼 |
| page_size | int | 每頁數量（預設 20，最大 500）|
| search | string | 全文搜尋 |

**Response:**
```json
{
  "count": 100,
  "next": "http://api/v1/questions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "subject": "刑法",
      "category": "總則",
      "question_type": "選擇題",
      "difficulty": "medium",
      "status": "published",
      "content": "題目內容...",
      "created_at": "2025-01-01T00:00:00Z",
      "created_by_username": "admin",
      "tags": [
        {"id": 1, "name": "刑法第271條", "question_count": 5, "created_at": "..."}
      ]
    }
  ]
}
```

---

### 3.2 取得題目詳細資訊

```
GET /api/v1/questions/{id}/
```

**Response:**
```json
{
  "id": 1,
  "subject": "刑法",
  "category": "總則",
  "question_type": "選擇題",
  "difficulty": "medium",
  "status": "published",
  "content": "題目內容...",
  "explanation": "解析說明...",
  "created_at": "2025-01-01T00:00:00Z",
  "created_by_username": "admin",
  "options": [
    {"id": 1, "content": "選項A", "is_correct": true, "order": 1},
    {"id": 2, "content": "選項B", "is_correct": false, "order": 2}
  ],
  "tags": [
    {"id": 1, "name": "刑法第271條", "question_count": 5, "created_at": "..."}
  ]
}
```

---

### 3.3 建立題目

```
POST /api/v1/questions/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| subject | string | ✓ | 科目 |
| category | string | | 分類 |
| question_type | string | | 題型（選擇題/是非題/申論題）|
| difficulty | string | | 難度（easy/medium/hard）|
| status | string | | 狀態（draft/published）|
| content | string | ✓ | 題目內容 |
| explanation | string | | 解析說明 |
| options | array | | 選項陣列 |
| tag_ids | array | | 標籤 ID 列表 |

**options 格式:**
```json
[
  {"content": "選項A", "is_correct": true, "order": 1},
  {"content": "選項B", "is_correct": false, "order": 2}
]
```

**Response (201):** 同取得題目詳細資訊

---

### 3.4 更新題目

```
PUT /api/v1/questions/{id}/
PATCH /api/v1/questions/{id}/
```

**Request Body:** 同建立題目

---

### 3.5 刪除題目

```
DELETE /api/v1/questions/{id}/
```

**Response:** `204 No Content`

---

### 3.6 批量建立題目

```
POST /api/v1/questions/bulk-create/
```

**Request Body:** 題目物件陣列

**Response:**
```json
{
  "results": [
    {"success": true, "id": 1, "data": {...}},
    {"success": false, "index": 1, "errors": "..."}
  ]
}
```

---

### 3.7 批量更新題目

```
PATCH /api/v1/questions/bulk-update/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| partial | boolean | 是否部分更新（預設 true）|

**Request Body:** 包含 `id` 的題目物件陣列

---

## 4. 標籤 (Tags)

### 4.1 取得標籤列表

```
GET /api/v1/tags/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| search | string | 搜尋標籤名稱 |

**Response:**
```json
[
  {
    "id": 1,
    "name": "刑法第271條",
    "question_count": 5,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

---

### 4.2 建立標籤

```
POST /api/v1/tags/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| name | string | ✓ | 標籤名稱 |

如果標籤已存在，回傳現有標籤。

---

### 4.3 取得/更新/刪除標籤

```
GET /api/v1/tags/{id}/
PUT /api/v1/tags/{id}/
PATCH /api/v1/tags/{id}/
DELETE /api/v1/tags/{id}/
```

---

## 5. 科目 (Subjects)

### 5.1 取得科目列表

```
GET /api/v1/subjects/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "刑法",
    "code": "criminal",
    "category": "法律",
    "description": "刑法相關題目",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

---

## 6. 考卷 (Exams)

### 6.1 取得考卷列表

```
GET /api/v1/exams/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "112年司律一試模擬",
    "description": "模擬測驗",
    "time_limit": 60,
    "created_by_admin": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "question_count": 50
  }
]
```

---

### 6.2 取得考卷詳細資訊

```
GET /api/v1/exams/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "112年司律一試模擬",
  "description": "模擬測驗",
  "time_limit": 60,
  "created_by_admin": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "exam_questions": [
    {
      "id": 1,
      "question": 1,
      "order": 1,
      "points": 2,
      "question_content": "題目內容...",
      "question_subject": "刑法",
      "question_category": "總則"
    }
  ]
}
```

---

### 6.3 建立考卷

```
POST /api/v1/exams/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| name | string | ✓ | 考卷名稱 |
| description | string | | 描述 |
| time_limit | int | | 時間限制（分鐘）|

---

### 6.4 更新/刪除考卷

```
PUT /api/v1/exams/{id}/
PATCH /api/v1/exams/{id}/
DELETE /api/v1/exams/{id}/
```

---

### 6.5 新增題目到考卷

```
POST /api/v1/exams/{id}/add_question/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| question | int | ✓ | 題目 ID |
| order | int | | 順序 |
| points | float | | 配分 |

---

### 6.6 從考卷移除題目

```
DELETE /api/v1/exams/{id}/remove_question/?exam_question_id={exam_question_id}
```

---

### 6.7 更新考卷中的題目

```
PATCH /api/v1/exams/{id}/update_question/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| exam_question_id | int | ✓ | 考卷題目關聯 ID |
| order | int | | 順序 |
| points | float | | 配分 |

---

### 6.8 取得歷史考卷

```
GET /api/v1/exams/historical/
```

---

### 6.9 開始考試

```
POST /api/v1/exams/{id}/start/
```

**Response:**
```json
{
  "exam_id": 1,
  "name": "112年司律一試模擬",
  "question_count": 50
}
```

---

### 6.10 依題目查詢考卷

```
GET /api/v1/exams/by_question/?question_id={id}
GET /api/v1/exams/by_questions/?question_ids={id1},{id2},{id3}
```

---

## 7. 模擬測驗 (Mock Exams)

### 7.1 產生模擬測驗

```
POST /api/v1/mock-exams/generate/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| name | string | | 測驗名稱 |
| subject_id | int | ✓* | 科目 ID（與 subject_name 擇一）|
| subject_name | string | ✓* | 科目名稱（與 subject_id 擇一）|
| question_count | int | | 題目數量（1-100，預設 20）|
| difficulty | string | | 難度（easy/medium/hard，預設 medium）|
| topic | string | | 主題篩選 |
| exam_year | int | | 年份篩選 |
| time_limit | int | | 時間限制（5-600 分鐘）|
| reuse_question_bank | boolean | | 是否從題庫抽選（預設 false，使用 AI 生成）|

**Response (201):**
```json
{
  "id": 1,
  "name": "刑法 模擬測驗",
  "subject": 1,
  "subject_name": "刑法",
  "question_count": 20,
  "time_limit": 60,
  "ai_generated": true,
  "generated_at": "2025-01-01T00:00:00Z",
  "exam": {...},
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

---

### 7.2 取得模擬測驗列表

```
GET /api/v1/mock-exams/
```

---

### 7.3 取得模擬測驗詳細資訊

```
GET /api/v1/mock-exams/{id}/
```

---

### 7.4 刪除模擬測驗

```
DELETE /api/v1/mock-exams/{id}/
```

---

### 7.5 從錯題生成測驗

```
POST /api/v1/mock-exams/from-wrong-questions/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| name | string | | 考卷名稱（預設：錯題複習測驗）|
| question_ids | array | | 題目 ID 列表（不提供則使用所有錯題）|
| limit | int | | 題目數量上限 |
| unreviewed_only | boolean | | 僅使用未複習的錯題（預設 false）|

---

### 7.6 從收藏生成測驗

```
POST /api/v1/mock-exams/from-bookmarks/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| name | string | | 考卷名稱（預設：收藏題目測驗）|
| question_ids | array | | 題目 ID 列表 |
| limit | int | | 題目數量上限 |

---

### 7.7 自訂測驗

```
POST /api/v1/mock-exams/custom/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| name | string | | 考卷名稱（預設：自訂測驗）|
| question_ids | array | ✓ | 題目 ID 列表 |
| time_limit | int | | 時間限制（分鐘）|

---

## 8. 考試結果 (Exam Results)

### 8.1 儲存考試結果

```
POST /api/v1/exam-results/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| exam_id | int | ✓ | 考卷 ID |
| score | int | ✓ | 分數（0-100）|
| correct_count | int | ✓ | 正確題數 |
| total_count | int | ✓ | 總題數 |
| duration_seconds | int | | 作答時間（秒）|
| wrong_question_ids | array | | 答錯的題目 ID 列表 |

**Response (201):**
```json
{
  "id": 1,
  "exam": 1,
  "exam_name": "112年司律一試模擬",
  "score": 80,
  "correct_count": 40,
  "total_count": 50,
  "duration_seconds": 3600,
  "completed_at": "2025-01-01T00:00:00Z"
}
```

---

### 8.2 取得考試結果列表

```
GET /api/v1/exam-results/
```

---

### 8.3 取得學習統計

```
GET /api/v1/exam-stats/
```

**Response:**
```json
{
  "total_answered": 500,
  "correct_answered": 400,
  "total_bank": 1000,
  "exam_count": 10,
  "average_score": 80.5,
  "accuracy": 80.0,
  "accuracy_trend": [
    {
      "date": "2025-01-01",
      "accuracy": 75.5,
      "exam_name": "刑法測驗",
      "exam_id": 1
    }
  ],
  "wrong_count": 50,
  "bookmark_count": 30,
  "top_wrong": [
    {
      "question_id": 1,
      "question_content": "題目內容...",
      "question_subject": "刑法",
      "wrong_count": 5,
      "reviewed": false
    }
  ]
}
```

---

## 9. 錯題本 (Wrong Questions)

### 9.1 取得錯題列表

```
GET /api/v1/wrong-questions/
```

**Response:**
```json
[
  {
    "id": 1,
    "question": 1,
    "question_content": "題目內容...",
    "question_subject": "刑法",
    "wrong_count": 3,
    "last_wrong_at": "2025-01-01T00:00:00Z",
    "reviewed": false
  }
]
```

---

### 9.2 標記為已複習

```
PATCH /api/v1/wrong-questions/{id}/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| reviewed | boolean | | 是否已複習（預設 true）|

---

### 9.3 刪除錯題記錄

```
DELETE /api/v1/wrong-questions/{id}/
```

---

## 10. 收藏 (Bookmarks)

### 10.1 取得收藏列表

```
GET /api/v1/bookmarks/
```

**Response:**
```json
[
  {
    "id": 1,
    "question": 1,
    "question_content": "題目內容...",
    "question_subject": "刑法",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

---

### 10.2 收藏題目

```
POST /api/v1/bookmarks/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| question_ids | array/int | ✓ | 題目 ID 或 ID 陣列 |

**Response (201):**
```json
{
  "bookmarked": [1, 2, 3]
}
```

---

### 10.3 取消收藏

```
DELETE /api/v1/bookmarks/{question_id}/
```

---

## 11. 快閃卡 (Flashcards)

### 11.1 取得快閃卡列表

```
GET /api/v1/flashcards/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| status | string | 狀態篩選（new/learning/review/mastered/due）|

**Response:**
```json
[
  {
    "id": 1,
    "question": 1,
    "question_subject": "刑法",
    "question_content": "題目內容...",
    "question_difficulty": "medium",
    "status": "learning",
    "ease_factor": 2.5,
    "interval": 1,
    "repetition": 0,
    "next_review_date": "2025-01-02",
    "last_reviewed_at": "2025-01-01T00:00:00Z",
    "review_count": 3,
    "is_due": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

---

### 11.2 建立快閃卡

```
POST /api/v1/flashcards/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| question | int | ✓ | 題目 ID |
| next_review_date | date | | 下次複習日期 |

---

### 11.3 刪除快閃卡

```
DELETE /api/v1/flashcards/{id}/
```

---

### 11.4 取得待複習卡片

```
GET /api/v1/flashcards/due/
```

---

### 11.5 複習卡片

使用 SM-2 演算法計算下次複習時間

```
POST /api/v1/flashcards/{id}/review/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| rating | int | ✓ | 評分（1-5）|

評分說明：
- 1: 完全不記得
- 2: 記得但很模糊
- 3: 記得一些
- 4: 記得大部分
- 5: 完全記得

---

### 11.6 取得統計資訊

```
GET /api/v1/flashcards/stats/
```

**Response:**
```json
{
  "total_cards": 100,
  "due_cards": 10,
  "completion_percent": 90.0,
  "review_streak": 7,
  "next_review_date": "2025-01-02"
}
```

---

### 11.7 取得複習歷史

```
GET /api/v1/flashcards/history/
```

**Response:**
```json
[
  {
    "id": 1,
    "rating": 4,
    "review_interval": 3,
    "reviewed_at": "2025-01-01T00:00:00Z"
  }
]
```

---

## 12. AI 功能 (AI Features)

### 12.1 AI 聊天

```
POST /api/v1/ai/chat/
```

**限制：** 免費版每日 10 次，進階版無限制

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| message | string | ✓ | 使用者訊息 |
| context_type | string | | 上下文類型（question/case）|
| context_id | int | | 上下文 ID（如題目 ID）|

**Response:**
```json
{
  "response": "AI 回應內容...",
  "chat_id": 1
}
```

---

### 12.2 取得聊天記錄

```
GET /api/v1/ai/history/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| limit | int | 返回記錄數量（預設 20）|
| offset | int | 偏移量（預設 0）|

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "message": "使用者訊息",
      "response": "AI 回應",
      "context_type": "question",
      "context_id": 1,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 12.3 AI 案例分析

```
POST /api/v1/ai/analyze-case/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| case_text | string | ✓ | 案例文字 |

**Response:**
```json
{
  "summary": "案例摘要...",
  "key_points": ["關鍵點1", "關鍵點2"],
  "related_laws": ["刑法第271條", "刑法第272條"]
}
```

---

### 12.4 申論題解析

```
POST /api/v1/essay-analysis/analyze/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| question_text | string | ✓ | 申論題目內容 |

**Response:**
```json
{
  "analysis": "【可能涉及的法條】\n...\n【學說見解】\n...",
  "chat_id": 1
}
```

---

### 12.5 取得申論解析記錄

```
GET /api/v1/essay-analysis/history/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| limit | int | 返回記錄數量（預設 20）|
| offset | int | 偏移量（預設 0）|

---

## 13. 申論題 (Essays)

### 13.1 提交申論題答案

```
POST /api/v1/essays/submit/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| subject | int | | 科目 ID |
| exam_year | int | | 考試年份 |
| exam_session | int | | 考試場次 |
| question_text | string | ✓ | 題目內容 |
| answer_text | string | ✓ | 答案內容 |

**Response (201):**
```json
{
  "id": 1,
  "user": 1,
  "username": "user",
  "subject": 1,
  "subject_name": "刑法",
  "exam_year": 112,
  "exam_session": 1,
  "question_text": "題目...",
  "answer_text": "答案...",
  "status": "pending",
  "submitted_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "grading": null
}
```

---

### 13.2 取得申論題列表

```
GET /api/v1/essays/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| subject | int | 科目 ID 篩選 |
| status | string | 狀態篩選（pending/grading/completed）|
| page | int | 頁碼 |

---

### 13.3 取得申論題詳細資訊

```
GET /api/v1/essays/{id}/
```

---

### 13.4 取得批改結果

```
GET /api/v1/essays/{id}/grading/
```

**Response:**
```json
{
  "id": 1,
  "essay_submission": 1,
  "essay_submission_info": {
    "id": 1,
    "subject": "刑法",
    "exam_year": 112
  },
  "score": 75.0,
  "max_score": 100.0,
  "percentage_score": 75.0,
  "feedback": "整體評語...",
  "strengths": "優點1\n優點2",
  "weaknesses": "缺點1\n缺點2",
  "suggestions": "建議1\n建議2",
  "grading_method": "ai",
  "graded_at": "2025-01-01T00:00:00Z"
}
```

---

## 14. 討論區 (Discussions)

### 14.1 取得討論列表

```
GET /api/v1/discussions/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| question | int | 題目 ID 篩選 |

**Response:**
```json
[
  {
    "id": 1,
    "question": 1,
    "question_subject": "刑法",
    "user": 1,
    "user_name": "user",
    "title": "討論標題",
    "content": "討論內容...",
    "parent": null,
    "upvotes": 10,
    "downvotes": 2,
    "score": 8,
    "status": "active",
    "is_flagged": false,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "replies": [...]
  }
]
```

---

### 14.2 建立討論

```
POST /api/v1/discussions/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| question | int | ✓ | 題目 ID |
| title | string | | 標題 |
| content | string | ✓ | 內容 |

---

### 14.3 回覆討論

```
POST /api/v1/discussions/{id}/reply/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| content | string | ✓ | 回覆內容 |

---

### 14.4 投票

```
POST /api/v1/discussions/{id}/vote/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| vote_type | string | ✓ | 投票類型（up/down）|

---

### 14.5 檢舉討論

```
POST /api/v1/discussions/{id}/report/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| reason | string | ✓ | 檢舉原因 |
| notes | string | | 備註 |

---

## 15. 遊戲化 (Gamification)

### 15.1 徽章

#### 取得所有徽章

```
GET /api/v1/gamification/badges/
```

#### 取得徽章詳細資訊

```
GET /api/v1/gamification/badges/{id}/
```

---

### 15.2 使用者徽章

#### 取得使用者獲得的徽章

```
GET /api/v1/gamification/user-badges/
```

**Response:**
```json
[
  {
    "id": 1,
    "badge": {
      "id": 1,
      "name": "初學者",
      "description": "完成第一次測驗",
      "icon": "starter",
      "points": 10
    },
    "awarded_at": "2025-01-01T00:00:00Z"
  }
]
```

---

### 15.3 經驗值 (XP)

#### 取得 XP 紀錄

```
GET /api/v1/gamification/user-xp/
```

**Response:**
```json
[
  {
    "id": 1,
    "source": "exam_complete",
    "delta": 100,
    "metadata": {"exam_id": 1},
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

#### 取得 XP 總計

```
GET /api/v1/gamification/user-xp/total/
```

**Response:**
```json
{
  "total_xp": 1500
}
```

---

### 15.4 學習小組

#### 取得小組列表

```
GET /api/v1/study-groups/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "刑法讀書會",
    "description": "一起準備刑法",
    "owner": 1,
    "visibility": "public",
    "max_members": 50,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "members_count": 10
  }
]
```

#### 建立小組

```
POST /api/v1/study-groups/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| name | string | ✓ | 小組名稱 |
| description | string | | 描述 |
| visibility | string | | 可見性（public/private）|
| max_members | int | | 人數上限 |

#### 加入小組

```
POST /api/v1/study-groups/{id}/join/
```

#### 離開小組

```
POST /api/v1/study-groups/{id}/leave/
```

---

### 15.5 通知排程

#### 取得通知列表

```
GET /api/v1/notifications/
```

#### 建立通知排程

```
POST /api/v1/notifications/
```

#### 更新/刪除通知

```
PUT /api/v1/notifications/{id}/
PATCH /api/v1/notifications/{id}/
DELETE /api/v1/notifications/{id}/
```

---

## 16. 學習分析 (Analytics)

### 16.1 學習進度

```
GET /api/v1/analytics/progress/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| time_range | string | 時間範圍（7/30/90/all）|

**Response:**
```json
{
  "overall": {
    "total_questions": 1000,
    "practiced_questions": 200,
    "progress_percentage": 20.0,
    "total_attempts": 500,
    "correct_attempts": 400,
    "accuracy": 80.0
  },
  "trend": [
    {
      "date": "2025-01-01",
      "attempts": 10,
      "correct": 8,
      "accuracy": 80.0
    }
  ]
}
```

---

### 16.2 科目分析

```
GET /api/v1/analytics/subjects/
```

**Response:**
```json
{
  "subjects": [
    {
      "subject_id": 1,
      "subject_name": "刑法",
      "subject_code": "criminal",
      "practiced": 50,
      "total_attempts": 100,
      "correct_attempts": 80,
      "accuracy": 80.0,
      "avg_time_spent": 45.5
    }
  ],
  "total_subjects": 5
}
```

---

### 16.3 學習趨勢

```
GET /api/v1/analytics/trends/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| days | int | 天數（預設 30）|

**Response:**
```json
{
  "trend_data": [
    {
      "date": "2025-01-01",
      "attempts": 10,
      "correct": 8,
      "accuracy": 80.0,
      "avg_time_spent": 45.5
    }
  ],
  "trend_direction": "improving",
  "recent_accuracy": 85.0,
  "earlier_accuracy": 75.0
}
```

---

### 16.4 學習建議

#### 取得建議列表

```
GET /api/v1/analytics/recommendations/
```

**Query Parameters:**
| 參數 | 類型 | 說明 |
|------|------|------|
| is_read | boolean | 是否已讀篩選 |
| priority | string | 優先級篩選 |

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "user": 1,
      "username": "user",
      "recommendation_type": "practice_schedule",
      "subject": 1,
      "subject_name": "刑法",
      "priority": "high",
      "content": "建議加強刑法的練習...",
      "generated_at": "2025-01-01T00:00:00Z",
      "is_read": false,
      "read_at": null
    }
  ]
}
```

#### 生成新建議

```
POST /api/v1/analytics/recommendations/
```

使用 AI 分析學習進度並生成新的學習建議。

#### 標記建議為已讀

```
PATCH /api/v1/analytics/recommendations/{id}/read/
```

---

### 16.5 學習指標

```
GET /api/v1/analytics/metrics/
POST /api/v1/analytics/metrics/
GET /api/v1/analytics/metrics/{id}/
PUT /api/v1/analytics/metrics/{id}/
PATCH /api/v1/analytics/metrics/{id}/
DELETE /api/v1/analytics/metrics/{id}/
```

---

### 16.6 模擬測驗表現

```
GET /api/v1/analytics/mock-performance/
POST /api/v1/analytics/mock-performance/
GET /api/v1/analytics/mock-performance/{id}/
PUT /api/v1/analytics/mock-performance/{id}/
PATCH /api/v1/analytics/mock-performance/{id}/
DELETE /api/v1/analytics/mock-performance/{id}/
```

---

## 17. 訂閱 (Subscription)

### 17.1 取得訂閱狀態

```
GET /api/v1/subscription/status/
```

**Response:**
```json
{
  "tier": "premium",
  "status": "active",
  "expires_at": "2025-02-01T00:00:00Z",
  "is_active": true
}
```

或免費版：
```json
{
  "tier": "free",
  "status": "free",
  "expires_at": null,
  "is_active": false
}
```

---

### 17.2 建立訂閱

```
POST /api/v1/subscription/create/
```

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| tier | string | ✓ | 訂閱等級（premium）|
| payment_intent_id | string | ✓ | Stripe Payment Intent ID |

**Response (201):**
```json
{
  "subscription_id": 1,
  "tier": "premium",
  "expires_at": "2025-02-01T00:00:00Z"
}
```

---

### 17.3 取消訂閱

```
POST /api/v1/subscription/cancel/
```

**Response:**
```json
{
  "message": "訂閱已取消",
  "subscription_id": 1
}
```

---

## 18. 擴充功能 (Extension)

Chrome 擴充功能專用 API

### 18.1 取得統計資訊

```
GET /api/v1/extension/stats/
```

**Response:**
```json
{
  "bookmarks_count": 30,
  "flashcards_count": 50,
  "practice_count": 100,
  "subscription_tier": "free"
}
```

---

### 18.2 同步書籤

```
POST /api/v1/extension/sync-bookmarks/
```

**Request Body:**
```json
{
  "bookmarks": [
    {
      "question_id": 1,
      "case_url": "https://...",
      "case_title": "判例標題"
    }
  ]
}
```

**Response:**
```json
{
  "synced_count": 5,
  "errors": []
}
```

---

### 18.3 同步快閃卡

```
POST /api/v1/extension/sync-flashcards/
```

**Request Body:**
```json
{
  "flashcards": [
    {
      "question_id": 1,
      "last_reviewed": "2025-01-01T00:00:00Z",
      "next_review": "2025-01-02T00:00:00Z",
      "ease_factor": 2.5,
      "interval": 3,
      "repetition": 2,
      "review_count": 5,
      "status": "learning"
    }
  ]
}
```

**Response:**
```json
{
  "synced_count": 3,
  "errors": []
}
```

---

## 19. PDF 解析 (PDF Parser)

### 19.1 解析試卷 PDF

```
POST /api/v1/extract-questions-pdf/
```

**Content-Type:** `multipart/form-data`

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| file | file | ✓ | 試卷 PDF 檔案 |

**Response:**
```json
{
  "count": 50,
  "level": "司法官",
  "category": "一試",
  "subject": "刑法",
  "time_length": 120,
  "questions": [
    {
      "number": 1,
      "content": "題目內容...",
      "options": [
        {"label": "A", "text": "選項A"},
        {"label": "B", "text": "選項B"}
      ]
    }
  ]
}
```

---

### 19.2 解析答案 PDF

```
POST /api/v1/extract-answers-pdf/
```

**Content-Type:** `multipart/form-data`

**Request Body:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| file | file | ✓ | 答案 PDF 檔案 |

**Response:**
```json
{
  "count": 50,
  "notes": "注意事項...",
  "answers": [
    {"question_number": 1, "answer": "A"},
    {"question_number": 2, "answer": "B"}
  ]
}
```

---

## 錯誤回應格式

所有 API 在發生錯誤時會回傳統一格式：

```json
{
  "error": "錯誤訊息"
}
```

或驗證錯誤：

```json
{
  "field_name": ["錯誤訊息1", "錯誤訊息2"]
}
```

### HTTP 狀態碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | 成功 |
| 201 | 建立成功 |
| 204 | 刪除成功（無內容）|
| 400 | 請求參數錯誤 |
| 401 | 未認證 |
| 403 | 無權限 |
| 404 | 資源不存在 |
| 429 | 請求過於頻繁 |
| 500 | 伺服器錯誤 |

---

## 認證方式

所有需要認證的 API 都需要在 Header 中加入 JWT Token：

```
Authorization: Bearer <access_token>
```

---

## API 文件互動介面

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- JSON Schema: `/swagger.json` 或 `/swagger.yaml`

