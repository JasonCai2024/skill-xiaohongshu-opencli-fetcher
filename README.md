# skill-xiaohongshu-opencli-fetcher

基于 **OpenCLI** 与桌面 Chrome 真实浏览器扩展桥接的小红书（XiaoHongShu）全能数据采集与分析技能。  
彻底告别传统爬虫频繁失效与抓包提取 Cookie 的繁琐操作，实现 **“免维护 Cookie、零风控风险、真实指纹、全能力覆盖”** 的小红书数据获取体验。

---

## GitHub 仓库信息

- **项目开源地址**：[https://github.com/JasonCai2024/skill-xiaohongshu-opencli-fetcher](https://github.com/JasonCai2024/skill-xiaohongshu-opencli-fetcher)
- **Git Clone 链接**：`git clone https://github.com/JasonCai2024/skill-xiaohongshu-opencli-fetcher.git`

---

## 业务流程图

```mermaid
flowchart TD
    UserReq["用户发起小红书抓取/分析指令"] --> Preflight["环境探活自检 (opencli doctor)"]
    Preflight --> CheckReady{"环境正常?"}
    CheckReady -->|"否"| Alert["自愈提示: 唤醒 Chrome 浏览器 / 扫码登录"]
    CheckReady -->|"是"| CheckLink{"输入是否为分享短链 (xhslink)?"}
    
    CheckLink -->|"是"| Resolve["resolve_shortlink.py 自动跟随 302 重定向"]
    CheckLink -->|"否"| Exec["进入核心命令调度"]
    Resolve --> Exec
    
    Exec --> S1["search: 关键词检索 (获取带 xsec_token 卡片)"]
    Exec --> S2["feed: 首页推荐流 (读取 SSR 内存快照)"]
    Exec --> S3["user: 博主作品列表 (获取主页公开笔记与封面)"]
    
    S1 & S2 & S3 --> DrillDown{"消费签名 URL 深入分析"}
    DrillDown --> C1["note: 提取单篇正文长文、互动数据与标签"]
    DrillDown --> C2["download: 批量下载多图原图 / 原始高清 MP4 视频"]
    DrillDown --> C3["comments: 抓取一级评论与楼中楼树状对话"]
    
    C1 & C2 & C3 --> Finish["数据清洗转码 ➔ 结构化呈现给大模型与用户"]
```

---

## 核心功能清单与输入输出速查表

| 功能模块 | 对应命令 | 输入参数（Input） | 输出数据（Output） | 核心业务价值 |
|---|---|---|---|---|
| **🔍 关键词搜索** | `search` | • `query`：关键词<br>• `--limit`：条数（默认 20） | • `rank`：排名序号<br>• `title`：笔记标题<br>• `author`：博主昵称<br>• `author_url`：博主签名主页<br>• `likes`：点赞数<br>• `published_at`：发布日期<br>• `url`：带 `xsec_token` 的笔记直链 | 行业热点追踪、爆款选题挖掘、对标竞品检索 |
| **🧭 首页推荐流** | `feed` | • `--limit`：条数（默认 20） | • `id`：笔记 ID<br>• `title`：笔记标题<br>• `type`：`normal` 图文 / `video` 视频<br>• `author`：博主昵称<br>• `likes`：点赞数<br>• `url`：带 `xsec_token` 的推荐流直链 | 平台算法风向感知、垂直领域最新素材监控 |
| **👤 博主主页作品** | `user` | • `id`：24 位博主 ID 或主页 URL 或**手机短链**<br>• `--limit`：条数（默认 15） | • `id`：笔记 ID<br>• `title`：作品标题<br>• `type`：图文/视频类型<br>• `likes`：点赞数<br>• `cover`：高清封面 CDN 原图直链<br>• `url`：带 `xsec_token` 的作品直链 | 对标博主深度调研、博主全部作品归档分析 |
| **📖 单篇正文详情** | `note` | • `note-id`：带 `xsec_token` 的笔记直链或**手机短链** | • `title`：完整标题<br>• `author`：作者昵称<br>• `content`：**全文长文正文（保留段落与格式）**<br>• `likes`：点赞数<br>• `collects`：收藏数<br>• `comments`：评论数<br>• `tags`：所有 `#话题标签` 列表 | 深度干货长文精读、Prompt 与行业方法论提炼 |
| **💾 媒体高清下载** | `download` | • `note-id`：带签名的笔记 URL 或**手机短链**<br>• `--output`：本地保存目录 | • **图文笔记**：按轮播顺序无水印原图（`1.jpg`, `2.jpg`...）<br>• **视频笔记**：原始 1080P/720P 高清 `.mp4` 视频与封面大图 | 多模态 Vision 大模型看图分析、Whisper 视频语音转文字 |
| **💬 楼中楼评论树** | `comments` | • `note-id`：带签名的笔记 URL<br>• `--with-replies`：是否展开楼中楼<br>• `--limit`：条数（默认 20） | • `author`：评论者昵称<br>• `userId`：用户 ID<br>• `text`：评论内容<br>• `likes`：点赞数<br>• `time`：发布时间 + **IP 归属省份/国家**<br>• `is_reply`：是否为楼中楼子回复<br>• `reply_to`：**被回复人昵称（树状追溯）**<br>• `images`：评论晒图 CDN 列表 | 用户真实痛点挖掘、舆情风向分析、评论区互动复刻 |
| **🔥 全量评论深度抓取** | `full_comments_fetcher.py` | • `url`：笔记 URL 或手机短链<br>• `--limit`：条数（支持 300/500/全量） | • `total`：采集评论总条数（实测可抓 **289+ 条**）<br>• `parentCount`：一级根楼层总数<br>• `comments`：包含全部楼中楼展开的多层级对话数组 | 突破单次 50 条上限，实现长笔记数百条全量评论地毯式采集 |
| **🔗 短链自动解析** | 内置中间件 | • 手机 App 复制的任意文案或 `xhslink` 短链 | • `type`：`user` 博主 / `note` 笔记<br>• `user_id`：24 位博主 ID<br>• `note_id`：24 位笔记 ID<br>• `full_url`：302 重定向后的标准签名长链 | 消除移动端与 PC 端差异，随手粘贴即可无感抓取 |

---

## 文件目录结构

```text
skill-xiaohongshu-opencli-fetcher/
├─ SKILL.md                              # 技能主工作说明书 (指令、约束与决策流)
├─ README.md                             # 本说明文件 (项目介绍、安装指引、决策表)
├─ .env.example                          # 凭据隔离规范示例
├─ .gitignore                            # 忽略本地临时文件与媒体产物
├─ scripts/
│  ├─ resolve_shortlink.py               # 移动端 302 分享短链自动解析中间件
│  ├─ full_comments_fetcher.py           # 全量评论深度抓取工具 (突破 50 条上限，实测抓 289+ 条)
│  └─ xhs_fetcher.py                     # 全功能 Python 封装与调度工具
└─ references/
   ├─ opencli-setup-guide.md             # 3 步环境安装与配置 SOP
   ├─ commands-reference.md              # 核心命令参数与实测数据结构手册
   └─ troubleshooting.md                 # 常见错误自愈排查指南
```

---

## 获取与安装配置说明（只需一次，终身免维护）

### 1. 前置依赖安装
确保系统已安装 Node.js（v18+），在终端执行：
```bash
npm install -g @jackwener/opencli
```

### 2. 安装 Chrome 浏览器扩展
- **途径 A（Chrome 网上应用店）**：直接在 Chrome Web Store 搜索 `OpenCLI` 安装并启用；
- **途径 B（本地解压加载）**：
  1. 运行 `opencli extension install`；
  2. 在 Chrome 打开 `chrome://extensions/` 开启开发者模式，点击“加载已解压的扩展程序”，选中 `~/.opencli/extension`。

### 3. 小红书账号登录与探活
1. 在已启用扩展的 Chrome 中打开 `https://www.xiaohongshu.com` 正常登录账号；
2. 终端执行探活命令：
   ```bash
   opencli doctor
   ```
   看到 `[OK] Connectivity: connected` 即表示全链路就绪！

---

## 凭证安全与隔离规范

本技能基于纯本地真实桌面浏览器扩展通信机制：
- **零凭证存储**：不记录、不保存、不上传任何 Cookie、Token、账号或密码；
- **环境隔离**：`.env.example` 为规范占位，`.gitignore` 严格忽略所有临时日志、媒体下载产物与本地凭证变体；
- **绝对安全**：一切请求完全继承您本机日常使用的真实浏览器指纹与安全会话。

---

## 核心设计决策对照表

| 决策维度 | 本技能方案 | 传统爬虫 / MCP 方案 | 核心优势 |
|---|---|---|---|
| **登录态维护** | **完全继承真实 Chrome** | 需抓包手动复制 Cookie | **终身免维护**，无需手动更新 Cookie |
| **风控对抗** | **原生真实浏览器指纹** | 无头浏览器 / 模拟 HTTP 请求 | 极难被小红书安全网关识别拦截 |
| **短链支持** | **内置 302 自动重定向解析** | 仅支持长链，短链必报错 | 用户随手粘贴手机分享文案即可直接识别 |
| **媒体提取** | **直接穿透嗅探原始 MP4/多图** | 页面加密流难以提取 | 批量下载无水印多图原图与 1080P MP4 视频 |
| **评论结构** | **树状还原楼中楼 (reply_to)** | 扁平乱序输出 | 完美还原评论区多人互动对话层级与 IP 属地 |
