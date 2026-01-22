# Supabase CLI 操作指南

本文件提供 Supabase CLI 的完整指令參考與標準作業流程，協助開發者進行環境建置、本地開發與資料庫同步。

## 1. 環境建置

在使用 Supabase CLI 之前，請確保已安裝 Docker Desktop 並確認其正在運行。

### 登入 Supabase
連結本地 CLI 至 Supabase 帳號。
```bash
npx supabase login
```

### 初始化專案
於專案根目錄建立 `supabase/` 設定檔夾。
```bash
npx supabase init
```

### 連結遠端專案
將本地環境連結至雲端專案。Project ID 可於 Supabase Dashboard 網址中取得。
```bash
npx supabase link --project-ref <your-project-id>
```

---

## 2. 本地開發流程

### 啟動本地環境
啟動 Docker 容器，包含 Postgres 資料庫、Studio 管理介面與 Edge Functions。
```bash
npx supabase start
```
*   Studio 預設網址：`http://localhost:54323`

### 停止本地環境
停止 Docker 容器運行。
```bash
npx supabase stop
```
*   若不需備份資料庫，可加上 `--no-backup` 參數加速關閉。

### 查看服務狀態
顯示所有本地服務的網址與 API 金鑰 (Anon/Service Role Keys)。
```bash
npx supabase status
```

---

## 3. 資料庫同步流程

### 從遠端更新至本地 (Remote to Local)
當遠端資料庫有變更（如其他成員更新或直接於 Dashboard 修改）時，需執行以下步驟同步至本地：

1.  **拉取遷移檔案**
    將遠端資料庫結構下載為本地遷移檔案 (migrations)。
    ```bash
    npx supabase db pull
    ```

2.  **重置本地資料庫**
    讀取 migration 檔案並重建本地資料庫結構。**此步驟為必要操作，單純 pull 不會更新運行中的容器。**
    ```bash
    npx supabase db reset
    ```

### 從本地推送到遠端 (Local to Remote)
當完成本地開發並需部署至雲端時：

1.  **產生遷移檔案**
    比對本地資料庫變更，建立新的 migration 檔案。
    ```bash
    npx supabase db diff -f <migration_name>
    ```

2.  **推送至遠端**
    將新的 migration 檔案套用至遠端資料庫。
    ```bash
    npx supabase db push
    ```

---

## 4. 進階與其他常用指令

### 建立空白遷移檔
手動建立一個新的 SQL migration 檔案。
```bash
npx supabase migration new <migration_name>
```

### 檢視遷移記錄
查看各個環境的遷移檔案套用狀態。
```bash
npx supabase migration list
```

### 產生型別定義 (TypeScript)
根據資料庫結構自動產生 TypeScript 型別定義檔。
```bash
npx supabase gen types typescript --local > src/types/supabase.ts
```

### 用戶端程式碼生成
產生不含 schema 的用戶端連結設定。
```bash
npx supabase gen types typescript --linked > src/types/supabase.ts
```

---

## 5. 常見問題排除

### 埠口衝突 (Port Already in Use)
若遇到 `failed to start docker container` 錯誤，通常為埠口佔用。
解決方式：
1. 執行 `npx supabase stop` 確保舊容器已關閉。
2. 重啟 Docker Desktop。
3. 檢查是否有其他 Postgres 服務佔用 5432 埠口。

### 推送無變化 (Remote database is up to date)
若修改了 SQL 函數內容 (Function Body) 但 `db push` 未偵測到變更：
解決方式：
1. 修改該 SQL 檔案 (如增加註解或空白行) 以改變檔案雜湊值。
2. 或建立新的 migration 檔案並重新定義該函數。
3. 執行 `npx supabase db push`。
