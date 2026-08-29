# 常见问题自愈与故障排查指南（Troubleshooting）

本手册指导 AI 助理与用户在遇到 OpenCLI 异常状态时快速定位并自愈。

---

## 故障排查自查表

| 错误代码 / 现象 | 根因分析 | 自愈排查步骤 |
|---|---|---|
| **`SERVICEHUB_AUTH_REQUIRED`**<br>(未配置会员凭据) | 本地 `.env` 中未配置 `SERVICEHUB_USERNAME` 或 `SERVICEHUB_PASSWORD` | 1. 复制 `.env.example` 为 `.env`<br>2. 填入您的 ServiceHub 远程地址与注册用户名、密码/Token<br>3. 或让 AI 助理协助写入 `.env` |
| **`SERVICEHUB_AUTH_FAILED`**<br>(会员鉴权失败) | 账号密码有误、远程服务器不可达或会员有效期已截止 | 1. 检查 `.env` 中的账号密码是否与 ServiceHub 平台一致<br>2. 确认 `SERVICEHUB_BASE_URL` 远程服务器网络畅通<br>3. 登录 ServiceHub 平台确认会员有效状态 |
| **`AUTH_REQUIRED`**<br>(小红书登录墙拦截) | Chrome 浏览器中的小红书登录态已过期，被 302 重定向到 `/login` | 1. 唤醒 Chrome 打开 `https://www.xiaohongshu.com`<br>2. 手机小红书 App 扫码登录账号<br>3. 登录成功后重新运行命令即可 |
| **`EXTENSION_DISCONNECTED`**<br>(扩展未连接) | Chrome 浏览器未启动，或 OpenCLI 扩展处于未启用状态 | 1. 打开 Chrome 浏览器<br>2. 访问 `chrome://extensions`<br>3. 检查 OpenCLI 扩展右下角开关是否处于开启状态 |
| **`DAEMON_OFFLINE`**<br>(守护进程未启动) | Node.js 后台守护进程未监听 19825 端口 | 终端执行：`opencli daemon restart` 或 `opencli doctor` 自动唤醒守护服务 |
| **`EMPTY_RESULT`**<br>(返回无数据) | 1. 传入了未解析的移动端短链 (`xhslink`)<br>2. 笔记已被作者删除/设为私密<br>3. 博主主页确实无公开笔记 | 1. 确认短链是否先调用了 `resolve_shortlink.py` 解析为长链<br>2. 尝试在 Chrome 浏览器中手动打开链接核验是否存在 |
| **`SECURITY_BLOCK`**<br>(安全限制拦截) | 传入了不带 `xsec_token` 的裸笔记 ID 触发了小红书网关拦截 | 必须先通过 `search` / `feed` / `user` 获取包含 `?xsec_token=...` 的签名 URL 再访问详情 |
| **评论抓取数少于元数据**<br>(显示300+却只抓几十条) | 1. 小红书 Web 端策略限制只展示 10 条根评论（全量需在 App 端看）<br>2. Desktop 模式隐藏了楼中楼展开按钮 | 1. **将 URL 域名替换为 `m.xiaohongshu.com`** 移动端模式抓取，自动展开楼中楼（样本量从 18 提升至 75+ 条）<br>2. 在报告中明确注明：API 元数据总数与 Web 实际采集样本覆盖率 |

---

## 快速自检命令
当怀疑环境状态时，执行一行命令即可查看全链路健康度：
```bash
opencli doctor
```
