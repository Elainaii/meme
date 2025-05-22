# 随机图片展示项目

这是一个基于Nuxt 3构建的随机图片展示应用。

## 功能特点

- 随机展示服务器中的图片
- 支持浅色/深色模式切换
- 响应式设计，适配移动端和桌面端

## 快速开始

### Windows用户一键启动

直接双击项目根目录中的`启动项目.bat`文件，它会自动安装依赖并启动项目。

### 手动安装与启动

1. **安装依赖**

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

2. **开发模式**

```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

3. **访问网站**

打开浏览器，访问 `http://localhost:3000`

### 常见问题排查

如果你看到"Welcome to Nuxt"的默认页面，而不是随机图片展示页面，可能是因为：

1. 项目没有正确加载app目录中的文件，确保在项目根目录运行命令
2. 访问 `http://localhost:3000/debug` 查看应用状态和路由信息
3. 确保nuxt.config.js中包含 `srcDir: 'app'` 配置

### 构建生产版本

```bash
npm run build
# 或
yarn build
# 或
pnpm build
```

### 启动生产版本

```bash
npm run start
# 或
yarn start
# 或
pnpm start
```

## 自定义图片

1. 将你的图片放入 `public/images` 目录
2. 修改 `app/components/RandomImage.vue` 文件中的 `fetchRandomImage` 函数

## 技术栈

- [Nuxt 3](https://nuxt.com/) - Vue框架
- [UnoCSS](https://github.com/unocss/unocss) - 原子CSS引擎
- [Vue Use](https://vueuse.org/) - Vue组合式API工具集
- [Color Mode](https://color-mode.nuxtjs.org/) - Nuxt颜色模式模块
