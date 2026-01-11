# ExamQuestionBank - 台灣律師國考智慧備考平台

## 專案背景與市場痛點

**ExamQuestionBank** 是一個專為台灣法律國家考試（司法官/律師考試）考生設計的一站式備考輔助平台。

### 現有問題
在現行的備考環境中，考生普遍面臨以下挑戰：

1. **資料分散且難以取得**  
   歷屆考古題散落在考選部與各大機構網站，考生需耗費大量時間搜尋、下載與整理 PDF 檔案，壓縮了實際研讀的時間。

2. **缺乏彈性練習機制**  
   傳統紙本或靜態檔案無法支援「跨年份」、「跨科目」的混合練習，考生難以針對個人弱項進行客製化的強化訓練。

3. **學習回饋斷層**  
   練習後缺乏即時的解析輔助，面臨艱澀考題時，往往需中斷學習流程去查閱書籍或網路資料。

4. **缺乏系統化記憶工具**  
   法條與實務見解的記憶量龐大，傳統死記硬背效率低落，且無法有效追蹤遺忘曲線。

本專案的開發初衷，即是透過技術手段解決上述繁瑣流程，讓考生能專注於「理解」與「記憶」本身。

---

## 核心功能

### 1. 智慧型自定義模擬考
**解決問題：** 傳統練習缺乏彈性，無法針對個人需求調整練習範圍。

**實作方式：**
- 考生可自選年份區間（如 105-112 年）與特定科目
- 系統從資料庫中即時抽取題目組合成專屬試卷
- 支援題目收藏、錯題追蹤與重複練習機制
- 自動儲存練習紀錄，供後續檢視與分析

**技術實作：**
- 前端使用 Vue Router 實現 `PracticeView`（練習模式）與 `UserExamView`（我的考卷）
- 透過 `mockExamService.js` 與 `examService.js` 處理考試資料流
- 後端 Django REST API 提供動態組卷邏輯與考試結果儲存

### 2. 系統化閃卡記憶
**解決問題：** 法條與實務見解記憶量龐大，缺乏有效的碎片化學習工具。

**實作方式：**
- 採用間隔重複（Spaced Repetition）演算法，自動計算下次複習時間
- 以滑動手勢為核心的流暢介面，類似原生 App 體驗
- 支援題目加入閃卡、自訂複習排程
- 提供複習進度追蹤與統計功能

**技術實作：**
- 前端使用 **Swiper.js** 實現流暢的卡片滑動效果
- `FlashcardView` 整合觸控手勢與動畫效果
- 後端實作 Spaced Repetition 演算法（見 `flashcards/models.py` 與 `flashcards/services.py`）
- 使用 Pinia 進行閃卡狀態管理

### 3. AI 申論解析
**解決問題：** 申論題解析資源不足，考生難以獲得即時回饋。

**實作方式：**
- 考生可針對申論題目呼叫 AI 進行解析
- AI 提供法律推論邏輯、解題思路與參考答案架構
- 支援多輪對話，深入探討法律概念

**技術實作：**
- 前端透過 `EssayAnalysisView` 與 `essayAnalysisService.js` 串接 AI
- 後端透過 `question_bank/essay_analysis_views.py` 處理 AI 請求
- 整合 OpenAI API 進行生成式 AI 回答

### 4. 學習追蹤與數據分析
**解決問題：** 考生缺乏量化工具追蹤學習進度與識別弱點。

**實作方式：**
- 自動統計答題正確率、各科目表現、錯題分布
- 視覺化圖表呈現學習曲線與進步幅度
- 提供科目別、年份別的詳細分析報告

**技術實作：**
- 前端使用 **Chart.js** 與 **vue-chartjs** 進行數據可視化
- `AnalyticsView` 整合多種圖表類型（折線圖、長條圖、圓餅圖）
- 後端 `analytics` app 提供完整的學習數據彙整 API
- 透過 `analyticsService.js` 進行前後端數據交換

### 5. 題庫管理系統
**解決問題：** 管理員需要高效的工具維護題庫資料。

**實作方式：**
- 支援題目新增、編輯、批次匯入
- 提供標籤管理、科目管理功能
- 整合 PDF 解析器，自動化試題上傳流程

**技術實作：**
- `AdminView` 提供完整的後台管理介面
- 使用 `pdfplumber` 解析 PDF 試題（見 `question_bank/services/pdf_parser.py`）
- Django Admin 與自訂 API 搭配使用

---

## 技術架構

### 前端技術堆疊
本專案採用現代化的前端技術，確保高效能與優質的使用者體驗。

| 技術 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | ^3.5.22 | 核心框架，使用 Composition API |
| **Vue Router** | ^4.2.5 | 頁面路由管理 |
| **Pinia** | ^2.1.7 | 狀態管理（替代 Vuex） |
| **Vite** | ^7.1.7 | 建構工具，提供快速的開發體驗 |
| **Bootstrap 5** | ^5.3.8 | 響應式佈局與元件庫 |
| **Swiper** | ^12.0.3 | 閃卡滑動效果 |
| **Chart.js** | ^4.5.1 | 學習數據視覺化 |
| **Axios** | ^1.6.2 | HTTP 請求處理 |
| **Vitest** | ^4.0.15 | 單元測試框架 |

**架構設計：**
- **元件化設計：** 將功能拆分為可重用的 Vue 元件（如 `QuestionList`、`QuestionItem`、`LoginModal`）
- **服務層抽象：** 所有 API 請求封裝於 `services/` 資料夾，便於維護與測試
- **響應式設計：** 支援桌機、平板、手機多種裝置
- **暗黑模式：** 內建淺色/深色主題切換功能

### 後端技術堆疊
後端專注於構建穩定、可擴展的 API 服務。

| 技術 | 版本 | 用途 |
|------|------|------|
| **Django** | 5.2.7 | 核心框架 |
| **Django REST Framework** | ^3.16.1 | RESTful API 建構 |
| **JWT** | ^5.3.1 | 無狀態身份驗證 |
| **Microsoft SQL Server** | - | 企業級資料庫 |
| **pdfplumber** | 0.11.7 | PDF 試題解析 |
| **OpenAI API** | ^1.0.0 | AI 功能整合 |
| **ChromaDB** | ^0.4.0 | 向量資料庫（預備 RAG） |
| **LangChain** | - | AI 應用框架（預備 RAG） |

**架構設計：**
- **模組化應用：** 將功能拆分為獨立的 Django App（`users`、`question_bank`、`exams`、`flashcards`、`analytics`）
- **RESTful API：** 遵循 REST 標準，提供清晰的 API 接口
- **權限管理：** 整合 JWT 與 Django Guardian 進行細緻的權限控制
- **資料完整性：** 使用 MSSQL 確保交易安全性
- **自動化流程：** 開發 PDF 解析腳本，降低人工維護成本

### 資料庫架構
專案採用關聯式資料庫設計，主要資料表包含：

- **Users：** 使用者資料與訂閱狀態
- **Questions：** 題目內容、標籤、科目、年份
- **Exams：** 考卷資料與題目關聯
- **MockExams：** 模擬考試紀錄
- **ExamResults：** 考試結果與答題紀錄
- **WrongQuestions：** 錯題本
- **Flashcards：** 閃卡與複習排程
- **Analytics：** 學習數據統計

---

## 專案結構

```
ExamQuestionBank/
├── ExamQuestionBank/          # Django 後端
│   ├── analytics/             # 學習數據分析模組
│   ├── discussions/           # 討論區（預備功能）
│   ├── exams/                 # 考試與模擬考管理
│   ├── flashcards/            # 閃卡系統（含 Spaced Repetition）
│   ├── gamification/          # 遊戲化功能（預備功能）
│   ├── question_bank/         # 題庫核心
│   │   ├── services/
│   │   │   ├── ai_service.py      # AI 服務整合
│   │   │   ├── pdf_parser.py      # PDF 解析器
│   │   │   └── rag_service.py     # RAG 功能（預備）
│   │   ├── ai_views.py            # AI API 端點
│   │   ├── essay_analysis_views.py # 申論分析 API
│   │   └── models.py
│   ├── users/                 # 使用者與訂閱管理
│   └── manage.py
│
├── frontend/                  # Vue 3 前端
│   ├── src/
│   │   ├── components/        # 可重用元件
│   │   │   ├── AIChatInterface.vue
│   │   │   ├── QuestionList.vue
│   │   │   ├── QuestionItem.vue
│   │   │   └── LoginModal.vue
│   │   ├── services/          # API 服務層
│   │   │   ├── aiService.js
│   │   │   ├── analyticsService.js
│   │   │   ├── examService.js
│   │   │   ├── flashcardService.js
│   │   │   └── mockExamService.js
│   │   ├── views/             # 頁面元件
│   │   │   ├── LandingView.vue
│   │   │   ├── PracticeView.vue
│   │   │   ├── UserExamView.vue
│   │   │   ├── FlashcardView.vue
│   │   │   ├── EssayAnalysisView.vue
│   │   │   ├── AnalyticsView.vue
│   │   │   └── AdminView.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
├── docs/                      # 專案文件
│   ├── API_DOCUMENTATION.md
│   └── model-relationships.md
│
└── requirements.txt
```

---

## 未來展望

### 擴充規劃
以下功能已完成後端基礎建設，待前端整合：

1. **RAG（Retrieval-Augmented Generation）整合**  
   - 後端已建置 LangChain、ChromaDB 與 OpenAI API 基礎設施
   - 目標：實現「基於真實法條與實務見解」的精準 AI 回答
   - 解決 AI 幻覺（Hallucination）問題，提升回答可信度

2. **遊戲化系統**  
   - 後端已建立 `gamification` app 與相關資料模型
   - 規劃：成就系統、排行榜、學習里程碑

3. **討論區與學習社群**  
   - 後端已建立 `discussions` app
   - 規劃：題目討論、學習筆記分享、考生交流

4. **訂閱與付費機制**  
   - 後端已建立訂閱管理系統（`users/subscription_views.py`）
   - 規劃：會員分級、進階功能解鎖

---

## 安裝與執行

### 後端（Django）

1. 安裝相依套件：
```bash
pip install -r requirements.txt
```

2. 設定環境變數（參考 `.env.example`）

3. 執行資料庫遷移：
```bash
python manage.py migrate
```

4. 啟動開發伺服器：
```bash
python manage.py runserver
```

### 前端（Vue）

1. 安裝相依套件：
```bash
cd frontend
npm install
```

2. 啟動開發伺服器：
```bash
npm run dev
```

3. 建置生產版本：
```bash
npm run build
```

---

## 專案特色

1. **前後端分離架構**  
   清晰的職責劃分，便於並行開發與獨立擴展。

2. **模組化設計**  
   功能拆分為獨立模組，提升程式碼可維護性與可測試性。

3. **響應式設計**  
   支援多種裝置，確保一致的使用體驗。

4. **資料驅動決策**  
   完整的學習數據追蹤與視覺化分析。

5. **自動化流程**  
   PDF 解析器大幅降低題庫維護成本。

6. **可擴展架構**  
   預留 RAG、遊戲化、社群功能的擴充空間。

---

## 授權

本專案採用 MIT 授權條款。
