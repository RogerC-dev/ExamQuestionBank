# 分支配置说明 (Branch Configuration Guide)

这个配置系统允许你在不同的 Git 分支中使用不同的后端配置，无需手动修改代码。

## 目录结构

```
src/config/
├── main/          # Main 分支配置 (Django 后端)
│   ├── api.js     # Django API 配置
│   ├── router.js  # Django 路由配置
│   └── services.js # Django 服务导出
└── supabase/      # Supabase 分支配置
    ├── api.js     # Supabase API 配置
    ├── router.js  # Supabase 路由配置
    └── services.js # Supabase 服务导出
```

## 当前分支配置

### Main 分支 (Django 后端)

主文件会自动导入 `config/main/` 中的配置：

- `services/index.js` → 导入 `@/config/main/services`
- `services/api.js` → 导入 `@/config/main/api`
- `router/index.js` → 导入 `@/config/main/router`

### Supabase 分支

在 Supabase 分支中，需要修改以下文件以导入 `config/supabase/` 中的配置：

1. **`services/index.js`** - 修改为：
   ```javascript
   export * from '@/config/supabase/services'
   ```

2. **`services/api.js`** - 修改为：
   ```javascript
   export { fetchSubjects, USE_SUPABASE } from '@/config/supabase/api'
   export { default } from '@/config/supabase/api'
   ```

3. **`router/index.js`** - 修改为：
   ```javascript
   export { default } from '@/config/supabase/router'
   ```

## 切换分支步骤

### 从 Main 切换到 Supabase 分支

1. 切换到 Supabase 分支：
   ```bash
   git checkout supabase
   ```

2. 修改三个主文件（如上所述）

3. 确保 `src/lib/supabase.js` 文件存在（Supabase 配置）

### 从 Supabase 切换到 Main 分支

1. 切换到 Main 分支：
   ```bash
   git checkout main
   ```

2. 主文件已经配置为使用 Django 配置，无需修改

## 配置内容

### Main 分支配置 (`config/main/`)

- **api.js**: Django REST API 配置，使用 Axios，JWT token 认证
- **router.js**: Django 认证检查（localStorage token）
- **services.js**: 导出 Django 服务（questionService, examService 等）

### Supabase 分支配置 (`config/supabase/`)

- **api.js**: Supabase Edge Functions API 配置
- **router.js**: Supabase 认证检查（Supabase session）
- **services.js**: 导出 Supabase 服务（Supabase RPC 版本）

## 注意事项

1. **不要提交配置切换的修改到错误的分支**
   - Main 分支应该始终使用 `config/main/`
   - Supabase 分支应该始终使用 `config/supabase/`

2. **服务文件位置**
   - Django 服务文件：`src/services/*.js` (非 Supabase 版本)
   - Supabase 服务文件：`src/services/*Supabase.js`

3. **共享文件**
   - 视图组件 (`views/`) 在两个分支中共享
   - 组件 (`components/`) 在两个分支中共享
   - 只有配置和服务层不同

## 版本控制建议

建议在 `.gitignore` 中确保：
- `config/main/` 和 `config/supabase/` 都被提交到 Git
- 主文件（`services/index.js`, `services/api.js`, `router/index.js`）的修改应该分别提交到对应的分支
