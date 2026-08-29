# 小红书 OpenCLI 数据获取助手（Skill: skill-xiaohongshu-opencli-fetcher）

> 专为 AI 智能体打造的**免维护、零风控、全功能**小红书数据采集与高价值评论深度分析技能。

---

## 📌 一、技能定位

本技能专门通过 **本地 OpenCLI 守护进程 + 桌面 Chrome 真实浏览器扩展**，为 AI 智能体提供安全合规的小红书全维度数据采集与深度分析能力。

### 🌟 3 大核心卖点：
- 🟢 **免维护 Cookie**：直接继承您本机日常使用的真实 Chrome 登录态，告别繁琐抓包与频繁失效的 Cookie；
- 🟢 **零风控封禁风险**：原生真实浏览器操作与指纹特征，非模拟 HTTP 爬虫协议，安全稳定；
- 🟢 **ServiceHub 会员专享**：核心调度与分析引擎采用 PyArmor 工业级二进制加密保护，专属于 ServiceHub 注册会员。

---

## ⚡ 二、能做什么 & 怎么对 AI 助理说（8 大核心能力）

用户无需记忆任何技术参数，**直接对 AI 助理说人话**即可触发对应能力；底层 CLI 命令同时为 AI 智能体提供标准调度规范：

| 核心能力 | 你可以这样向 AI 助理说（自然语言触发） | 底层执行命令（AI 智能体调度） |
|---|---|---|
| 🔍 **关键词搜索** | *“搜一下小红书上关于 **DeepSeek 实操** 的热门笔记”* | `opencli xiaohongshu search "<query>" --limit 20 -f yaml` |
| 🏠 **首页推荐流** | *“抓一下现在小红书**首页推荐**的前 20 篇笔记”* | `opencli xiaohongshu feed --limit 20 -f yaml` |
| 👤 **博主主页作品** | *“看看**这个博主**的所有笔记：`https://xhslink.cn/m/xxx`”* | `opencli xiaohongshu user <博主ID> --limit 15 -f yaml` |
| 📝 **单篇笔记正文** | *“把**这篇笔记**的完整正文和文案读出来：`<链接>`”* | `opencli xiaohongshu note "<签名URL>" -f yaml` |
| 📥 **多图/视频下载** | *“把这篇笔记的**无水印图片/高清视频**下载到 `D:/xhs/`”* | `opencli xiaohongshu download "<签名URL>" --output "<目录>" -f yaml` |
| 💬 **快速评论抽样** | *“抓一下这篇笔记的评论区对话（快速模式）”* | `opencli xiaohongshu comments "<签名URL>" --with-replies -f yaml` |
| 🔥 **全量深度抓取** | *“抓这篇笔记的全部评论，递归展开所有楼中楼”* | `python scripts/full_comments_fetcher.py "<URL>" --limit 500` |
| 🧠 **高价值评论分析** | *“**分析这篇笔记的评论区**，提炼需求、同行引流和行业内幕”* | `python scripts/analyze_comments.py "<URL>" --title "<标题>"` |
| 🔗 **短链自动解析** | *“把这个手机分享短链解析成长链：`https://xhslink.cn/a/xxx`”* | `python scripts/resolve_shortlink.py "<短链>"` |

---

## 💡 三、典型使用流程（3 个拿来即用的实战场景）

### 场景 1：行业热点追踪 + 爆款长文精读
> 💬 **用户需求**：*“帮我搜一下小红书上关于‘AI 智能体实战’的热门笔记，并把点赞最高的一篇正文完整读出来。”*
* **AI 助理自动执行**：
  1. 执行 `search "AI 智能体实战"` 获取热门笔记列表及官方 `xsec_token` 签名长链；
  2. 自动选取点赞排名前 1 的笔记链接；
  3. 执行 `note <签名URL>` 提取完整长文正文、段落标签与互动指标；
  4. 为您提炼核心方法论与实操要点。

### 场景 2：对标博主一键深度调研
> 💬 **用户需求**：*“我想调研这个博主的所有作品：`https://xhslink.cn/m/uWP0uFkbut`”*
* **AI 助理自动执行**：
  1. 自动调用 `resolve_shortlink.py` 解析手机短链，逆向提取出 24 位博主 ID；
  2. 执行 `user <博主ID>` 批量抓取该博主近期发布的 15 篇图文与视频作品；
  3. 为您结构化梳理其选题方向、爆款规律与封面视觉风格。

### 场景 3：爆款评论区 100% 全景原声洞察
> 💬 **用户需求**：*“请对这篇爆款笔记的评论区进行分析：`<笔记链接>`”*
* **AI 助理自动执行**：
  1. 调用 `full_comments_fetcher.py` 驱动浏览器递归展开全部楼中楼子回复（抓满 140+ 条 Web 极限数据）；
  2. 自动过滤 40% 的比心、纯表情等无实质水评；
  3. 按照 **《高价值评论分析框架》** 自动输出包含【需求痛点】、【同行截流】、【实质争议】、【行业内幕】与【人群靶向切片】的 3 大板块全景报告。

---

## 🛠️ 四、首次使用配置（只需 1 次，终身免维护）

### 1. 🔒 配置 ServiceHub 会员凭证（核心门禁）
本技能核心底层驱动受 ServiceHub 会员体系保护，使用前请配置您的会员账号：
1. 复制根目录的 `.env.example` 为 `.env`；
2. 填入您的 ServiceHub 远程服务器地址与会员账号密码：
   ```env
   SERVICEHUB_BASE_URL=http://localhost:8000
   SERVICEHUB_USERNAME=您的ServiceHub会员账号
   SERVICEHUB_PASSWORD=您的ServiceHub密码或Token
   ```
*(注：若未配置，AI 智能体会主动友好提示并协助您写入)*

### 2. 安装前置依赖
确保系统已安装 Node.js（v18+），在终端执行：
```bash
npm install -g @jackwener/opencli
```

### 3. 安装 Chrome 浏览器扩展
- **途径 A（Chrome 网上应用店）**：直接在 Chrome Web Store 搜索 `OpenCLI` 安装并启用；
- **途径 B（本地解压加载）**：
  1. 运行 `opencli extension install`；
  2. 在 Chrome 打开 `chrome://extensions/` 开启开发者模式，点击“加载已解压的扩展程序”，选中 `~/.opencli/extension`。

### 4. 账号登录与一键探活
1. 在已启用扩展的 Chrome 中打开 `https://www.xiaohongshu.com` 正常登录账号；
2. 终端执行探活命令：
   ```bash
   opencli doctor
   ```
   看到 `[OK] Connectivity: connected` 即表示全链路就绪！

---

## 🔍 五、常见问题与自愈排查表

| 错误代码 / 现象 | 根因分析 | 极简自愈排查步骤 |
|---|---|---|
| **`SERVICEHUB_AUTH_REQUIRED`**<br>(未配置会员凭据) | 本地 `.env` 中未配置 `SERVICEHUB_USERNAME` 或密码 | 1. 复制 `.env.example` 为 `.env`<br>2. 填入您的 ServiceHub 账号密码，或让 AI 助理协助写入 |
| **`SERVICEHUB_AUTH_FAILED`**<br>(会员鉴权失败) | 账号密码输入有误或会员已到期 | 1. 检查 `.env` 中的账号密码是否正确<br>2. 登录 ServiceHub 平台检查会员有效状态 |
| **`AUTH_REQUIRED`**<br>(小红书登录墙拦截) | Chrome 浏览器中的小红书登录态已过期 | 1. 打开 Chrome 访问 `xiaohongshu.com`<br>2. 手机小红书 App 扫码登录并刷新即可 |
| **`EXTENSION_DISCONNECTED`**<br>(扩展未连接) | Chrome 浏览器未打开或插件未启用 | 1. 打开 Chrome 浏览器<br>2. 访问 `chrome://extensions` 确认 OpenCLI 开关开启 |
| **`EMPTY_RESULT`**<br>(返回无数据) | 笔记被作者删除或传入了不合规链接 | 1. 确认短链是否先经过解析<br>2. 在 Chrome 中手动打开核验笔记是否存在 |

---

## ⚠️ 六、平台级数据边界与评论抓取限制说明（AI 助理必读）

当使用本技能分析小红书笔记评论时，**请知晓以下平台级 Web 规则**，避免产生“为什么拿不到 300+ 全量”的误解：

1. **元数据总数（如 376 条） vs Web 物理抓取上限（约 140~150 条）**：
   - `note` 命令获取的 `comments: 376` 是小红书后台记录的历史全量总数；
   - 小红书为了防全量爬取并强推 App 导流，在 Web 网页端（PC/手机网页）**只下发前 10 个核心主话题楼层（`.parent-comment`）**；
   - 本技能通过平滑触底与楼中楼多轮递归展开，能够将这 10 个主楼层下包含的全部 **130+ 条楼中楼子回复全部提取**，最终稳定获取 **约 140~150 条高质量真实评论（样本覆盖率约 38%）**；
   - 剩余 62% 的一级长尾评论受平台导流策略限制，**仅在手机小红书 App 内滑动开放**。
2. **为什么 140~150 条已完全满足爆款拆解与舆情洞察？**
   - 小红书算法已将全篇**点赞最高、互动最多、争议最激烈的前 10 大核心楼层**置于首屏；
   - 所有全网爆款热评（80+ 赞、50 赞、40 赞等最能代表用户核心痛点与共识的评论）**100% 囊括在抓取的 140~150 条样本中**，足以支撑 100% 的高质量自媒体拆解与商业画像分析。

---

## 🔒 七、凭证安全与隔离规范

本技能基于纯本地真实桌面浏览器扩展通信机制：
- **小红书零凭证存储**：不记录、不保存、不上传任何小红书 Cookie、Token、账号或密码；
- **ServiceHub 鉴权隔离**：本地 `.env` 严格被 `.gitignore` 忽略，安全隔离会员私有凭据；
- **环境绝对安全**：一切小红书请求完全继承您本机日常使用的真实浏览器指纹与安全会话。

---

## 📊 八、核心设计决策对照表

| 决策维度 | 本技能方案 | 传统爬虫 / MCP 方案 | 核心优势 |
|---|---|---|---|
| **登录态维护** | **完全继承真实 Chrome** | 需抓包手动复制 Cookie | **终身免维护**，无需手动更新 Cookie |
| **风控对抗** | **原生真实浏览器指纹** | 无头浏览器 / 模拟 HTTP 请求 | 极难被小红书安全网关识别拦截 |
| **短链支持** | **内置 302 自动重定向解析** | 仅支持长链，短链必报错 | 用户随手粘贴手机分享文案即可直接识别 |
| **媒体提取** | **直接穿透嗅探原始 MP4/多图** | 页面加密流难以提取 | 批量下载无水印多图原图与 1080P MP4 视频 |
| **评论结构** | **树状还原楼中楼 (reply_to)** | 扁平乱序输出 | 完美还原评论区多人互动对话层级与 IP 属地 |
| **评论上限** | **穷尽 Web 极限 (140~150条)** | 仅能取 10~18 条 | 自动递归展开全部楼中楼，达到 Web 物理极限 |
| **商业保护** | **PyArmor 9.x 核心加密** | 源码完全裸奔 | 100% 锁定 ServiceHub 会员专属授权 |

---

## 📁 九、文件目录结构

```text
skill-xiaohongshu-opencli-fetcher/
├─ SKILL.md                              # 技能主工作说明书 (指令、约束、决策流与 AI 引导准则)
├─ README.md                             # 本说明文件 (用户友好说明书、提示词指南与架构手册)
├─ .env.example                          # ServiceHub 会员凭据配置模板
├─ .gitignore                            # 忽略本地临时文件与私有源码
├─ scripts/
│  ├─ _xhs_core/                         # 🔒 [加密] 核心底层驱动与分析引擎 (PyArmor 加密包)
│  ├─ resolve_shortlink.py               # 移动端 302 分享短链自动解析外壳
│  ├─ full_comments_fetcher.py           # 全量评论深度抓取工具外壳 (Web 极限 140~150 条)
│  ├─ analyze_comments.py                # 爆款高价值评论全景深度分析与 3 板块报告生成器
│  └─ xhs_fetcher.py                     # 全功能 Python 统一调用门面
└─ references/
   ├─ opencli-setup-guide.md             # 3 步环境安装与配置 SOP
   ├─ commands-reference.md              # 核心命令参数与实测数据结构手册
   ├─ comment-analysis-framework.md      # 小红书爆款高价值评论全景分析框架标准
   └─ troubleshooting.md                 # 常见错误自愈排查指南
```
