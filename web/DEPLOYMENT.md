# 前端部署配置指南

## API域名配置

前端项目使用环境变量来配置API地址，您可以通过以下方式修改：

### 方法1：使用 .env 文件（推荐）

1. 复制 `.env.example` 文件为 `.env`
2. 修改 `.env` 文件中的API地址：

```env
# 生产环境API基础URL
NUXT_PUBLIC_API_BASE_URL=https://your-domain.com/api

# 开发环境API基础URL (可选)
NUXT_PUBLIC_DEV_API_BASE_URL=http://localhost:8000
```

### 方法2：使用环境变量

在部署时设置环境变量：

```bash
# Windows (PowerShell)
$env:NUXT_PUBLIC_API_BASE_URL="https://your-domain.com/api"

# Linux/Mac
export NUXT_PUBLIC_API_BASE_URL="https://your-domain.com/api"
```

## 部署步骤

1. 配置API地址（见上述方法）
2. 安装依赖：`pnpm install`
3. 构建生产版本：`pnpm build`
4. 启动生产服务器：`pnpm start`

## 注意事项

- 确保API地址包含正确的协议（http:// 或 https://）
- 生产环境建议使用HTTPS
- API地址不需要尾部斜杠
