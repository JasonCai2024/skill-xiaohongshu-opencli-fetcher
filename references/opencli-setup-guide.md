# OpenCLI 安装、配置与使用环境搭建指南

本指南用于指导用户与 AI 助理首次配置 OpenCLI 小红书运行环境。配置只需一次，终身免维护 Cookie。

---

## 核心架构原理

OpenCLI 采用 **“Node.js 后台守护进程 + Chrome 桌面浏览器插件”** 架构：
1. **Node.js Daemon**：常驻后台监听本地 `127.0.0.1:19825` 端口；
2. **Chrome 扩展程序**：无感桥接用户日常使用的真实 Chrome 浏览器；
3. **数据请求放行**：小红书服务端接收到来自真实浏览器指纹与正常登录账号的访问，判定为真人放行数据，彻底消除封号与验证码风险。

---

## 3 步快速配置 SOP

### 第 1 步：安装 Node.js 与 OpenCLI CLI
1. 确保电脑已安装 [Node.js](https://nodejs.org/)（推荐 v18+）；
2. 在系统终端执行全局安装：
   ```bash
   npm install -g @jackwener/opencli
   ```

### 第 2 步：安装并启用 Chrome 浏览器扩展
- **途径 A（推荐，Chrome 网上应用店）**：
  在 Chrome Web Store 中直接搜索 `OpenCLI` 安装并开启扩展。
- **途径 B（本地解压安装）**：
  1. 终端执行：`opencli extension install`（会自动下载扩展至 `~/.opencli/extension`）；
  2. 在 Chrome 地址栏打开 `chrome://extensions/`（Edge 打开 `edge://extensions/`）；
  3. 开启右上角 **「开发者模式」**；
  4. 点击 **「加载已解压的扩展程序」**，选中 `~/.opencli/extension` 目录。

### 第 3 步：登录小红书账号并验证
1. 打开已启用扩展的 Chrome 浏览器，访问 `https://www.xiaohongshu.com`；
2. 正常扫码登录您的小红书账号；
3. 打开终端执行环境自检命令：
   ```bash
   opencli doctor
   ```
4. **正常就绪输出**：
   ```text
   [OK] Daemon: running on port 19825
   [OK] Extension: connected
   [OK] Connectivity: connected in 1.2s
   ```
5. 验证登录身份：
   ```bash
   opencli xiaohongshu whoami -f yaml
   ```

---

## 日常使用说明
- 日常使用时，只要 **Chrome 浏览器保持打开** 且小红书账号处于登录状态，即可随时在任意终端或 AI Agent 中无感调用抓取命令，无需任何手动介入。
