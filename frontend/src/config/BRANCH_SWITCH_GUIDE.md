# 分支切换指南 (Branch Switch Guide)

## 快速切换步骤

### 切换到 Supabase 分支

1. **切换到 Supabase 分支**
   ```bash
   git checkout supabase
   ```

2. **修改三个主文件**

   **`src/services/index.js`** - 改为：
   ```javascript
   /**
    * Service Index - Supabase Branch
    */
   export * from '@/config/supabase/services'
   ```

   **`src/services/api.js`** - 改为：
   ```javascript
   /**
    * API Service - Supabase Branch
    */
   export { fetchSubjects, USE_SUPABASE } from '@/config/supabase/api'
   export { default } from '@/config/supabase/api'
   ```

   **`src/router/index.js`** - 改为：
   ```javascript
   /**
    * Router - Supabase Branch
    */
   export { default } from '@/config/supabase/router'
   ```

3. **确保 Supabase 配置文件存在**
   - 确保 `src/lib/supabase.js` 存在
   - 确保所有 Supabase 服务文件存在（`*Supabase.js`）

### 切换回 Main 分支

1. **切换到 Main 分支**
   ```bash
   git checkout main
   ```

2. **主文件已经配置好**
   - `src/services/index.js` 已经导入 `@/config/main/services`
   - `src/services/api.js` 已经导入 `@/config/main/api`
   - `src/router/index.js` 已经导入 `@/config/main/router`
   - 无需修改！

## 文件对应关系

### Main 分支 (当前)
- `services/index.js` → `config/main/services.js`
- `services/api.js` → `config/main/api.js`
- `router/index.js` → `config/main/router.js`

### Supabase 分支
- `services/index.js` → `config/supabase/services.js`
- `services/api.js` → `config/supabase/api.js`
- `router/index.js` → `config/supabase/router.js`

## 注意事项

1. **不要提交错误的配置到错误的分支**
   - 在 Main 分支提交前，确保使用的是 `config/main/`
   - 在 Supabase 分支提交前，确保使用的是 `config/supabase/`

2. **配置文件夹是共享的**
   - `config/main/` 和 `config/supabase/` 都在两个分支中
   - 只有三个主文件（`services/index.js`, `services/api.js`, `router/index.js`）需要根据分支修改

3. **服务文件位置**
   - Django 服务：`src/services/*.js` (非 Supabase 版本)
   - Supabase 服务：`src/services/*Supabase.js`
   - 两个分支都包含所有服务文件，但通过配置选择使用哪个

## 验证配置

切换分支后，可以通过以下方式验证：

1. **检查导入路径**
   - 打开 `services/index.js`，确认导入的是正确的配置文件夹

2. **检查控制台**
   - 启动开发服务器，检查是否有导入错误

3. **测试功能**
   - 尝试登录，确认使用的是正确的后端
