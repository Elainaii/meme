# 随机梗图展示

## 项目简介

这是一个基于 FastAPI + Nuxt.js 开发的随机梗图展示系统，支持图片上传、审核和随机展示功能。用户可以上传有趣的梗图，管理员可以审核图片，访客可以随机浏览已审核的图片。

## 网址

[随机梗图～(∠・ω< )⌒★](https://graywitch.xyz/)
## 主要功能

### 🎯 核心功能
- **随机图片展示**：随机展示一张已审核的梗图
- **图片上传**：支持拖拽上传多张图片
- **图片审核**：管理员可以审核待审核图片
- **图床集成**：使用 PicGo 图床服务展示图片
![[1.png]]
![[2.png]]
### 🎨 用户体验
- **响应式设计**：适配移动端和桌面端
- **暗色模式**：支持明暗主题切换
- **平滑动画**：图片切换时的尺寸过渡动画
- **预加载机制**：提前加载下一张图片，提升用户体验

### 🔧 管理功能
- **管理员登录**：安全的 JWT 认证
- **图片管理**：查看待审核和已审核图片
- **批量操作**：支持图片的通过/删除操作
- **分页浏览**：高效的分页展示机制
![[3.png]]
![[4.png]]
## 技术栈

### 后端
- **FastAPI**
- **SQLAlchemy**
- **MySQL**

### 前端
- **Nuxt.js 3**
- **Vue 3**

## 项目结构

```
meme/
├── server/                 # 后端代码
│   ├── main.py            # 主应用入口
│   ├── config.py          # 配置文件
│   ├── database.py        # 数据库模型
│   ├── models.py          # Pydantic 模型
│   ├── auth.py            # 认证逻辑
│   ├── routers/           # API 路由
│   │   ├── images.py      # 图片相关接口
│   │   ├── upload.py      # 上传接口
│   │   └── admin.py       # 管理接口
│   ├── services/          # 业务服务
│   │   └── picgo_service.py # PicGo 图床服务
│   └── utils/             # 工具函数
│       └── image_utils.py # 图片处理工具
├── web/                   # 前端代码
│   ├── app/               # Nuxt.js 应用
│   │   ├── components/    # Vue 组件
│   │   │   ├── RandomImage.vue    # 随机图片组件
│   │   │   ├── ImageUploader.vue  # 图片上传组件
│   │   │   ├── AppHeader.vue      # 应用头部
│   │   │   └── AppFooter.vue      # 应用底部
│   │   ├── pages/         # 页面
│   │   │   ├── index.vue  # 首页
│   │   │   ├── login.vue  # 登录页
│   │   │   └── admin/     # 管理页面
│   │   ├── stores/        # 状态管理
│   │   └── utils/         # 工具函数
│   └── nuxt.config.js     # Nuxt 配置
└── images/                # 图片存储目录
    ├── checked/           # 已审核图片
    └── unchecked/         # 待审核图片
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- pnpm（推荐）或 npm

### 后端启动

1. 进入 server 目录
```bash
cd server
```

2. 复制环境变量文件
```bash
cp .env.example .env
```

3. 编辑 `.env` 文件，配置必要参数：
```env
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=your-admin-password
PICGO_API_URL=your-picgo-api-url
PICGO_API_KEY=your-picgo-api-key
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

5. 启动服务
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动

### 前端启动

1. 进入 web 目录
```bash
cd web
```

2. 复制环境变量文件
```bash
cp .env.example .env
```

3. 编辑 `.env` 文件：
```env
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

4. 安装依赖
```bash
pnpm install
```

5. 启动开发服务器
```bash
pnpm run dev
```

前端服务将在 `http://localhost:3000` 启动

## API 接口

### 图片相关
- `GET /image` - 获取随机图片
- `POST /upload/` - 上传图片
- `GET /image/{image_id}` - 获取指定图片
- `GET /image/unchecked/{image_id}` - 获取未审核图片

### 管理接口
- `POST /admin/login` - 管理员登录
- `GET /admin/pending-images` - 获取待审核图片
- `GET /admin/checked-images` - 获取已审核图片
- `POST /image/{image_id}/check` - 审核图片
- `DELETE /admin/image/{image_id}` - 删除图片

### PicGo 图床
- `POST /picgo/upload` - 上传到 PicGo 图床
- `POST /picgo/upload-url` - 通过 URL 上传到图床
## 部署说明

### 生产环境配置

1. **后端部署**
   - 修改 `.env` 中的配置
   - 使用 Gunicorn 或 uWSGI 部署
   - 配置反向代理（Nginx）
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # API 代理到 FastAPI 后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 直接代理后端 API（如果前端直接调用后端）
    location ~ ^/(image|upload|admin|health) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    
    # Nuxt 3 前端应用代理
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }
}
```

2. **前端部署**
   - 修改 API 地址配置
   - 构建生产版本：`pnpm build`
   - 部署到静态文件服务器或 Nuxt 服务器

3. **数据库**
   - 生产环境建议使用 MySQL
   - 修改 `DATABASE_URL` 配置

## 配置说明

### 后端配置 (server/.env)
```env
# JWT 配置
SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 管理员密码
ADMIN_PASSWORD=your-admin-password

# 数据库配置
DATABASE_URL=sqlite:///./meme.db

# PicGo 图床配置（可选）
PICGO_API_URL=your-picgo-api-url
PICGO_API_KEY=your-picgo-api-key

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False
```

### 前端配置 (web/.env)
```env
# API 配置
NUXT_PUBLIC_API_BASE_URL=https://your-domain.com/api
NUXT_PUBLIC_DEV_API_BASE_URL=http://localhost:8000

# 上传配置
NUXT_PUBLIC_MAX_UPLOAD_FILES=9
```

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- GitHub: [项目地址](https://github.com/Elainaii/meme)
- 问题反馈: [Issues](https://github.com/Elainaii/meme/issues)

## 友链

[Kutius/steam-judger: Steam 游戏库终极审判，AI 法官在此！](https://github.com/Kutius/steam-judger)

---

*Ciallo～(∠・ω< )⌒★*