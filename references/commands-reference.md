# OpenCLI 小红书命令全量参考手册

本文档记录 OpenCLI 小红书各子命令的精确入参、参数修饰符以及经真实环境实测的 100% 对应数据结构。

---

## 一、命令清单与流水线分类

| 命令 | 分类 | 功能描述 | 依赖前提 |
|---|---|---|---|
| `doctor` | 探活诊断 | 检查后台 Daemon 与 Chrome 扩展连接状态 | 无 |
| `search` | 前置列表 | 关键词检索前 20 条笔记卡片与博主签名链接 | 需已登录 |
| `feed` | 前置列表 | 获取首页个性化推荐流（包含图文/视频类型） | 需已登录 |
| `user` | 前置列表 | 抓取指定博主主页最新 15 篇作品与高清封面 | 需已登录 |
| `note` | 后置消费 | 读取单篇笔记正文长文、点赞/收藏数据与话题标签 | 需传入带签名 URL |
| `download` | 后置消费 | 批量下载图文所有多图原图或原始高清 MP4 视频 | 需传入带签名 URL |
| `comments` | 后置消费 | 抓取单篇笔记全部一级评论与楼中楼子回复对话树 | 需传入带签名 URL |

---

## 二、各命令调用与实测数据结构

### 1. `search`（关键词搜索）
```bash
opencli xiaohongshu search "DeepSeek" --limit 20 -f yaml
```
**实测返回结构**：
```yaml
- rank: 1
  title: 中国头部大模型创始人图鉴
  author: 苏倩
  author_url: https://www.xiaohongshu.com/user/profile/641f027a0000000011023304?channel_type=web_search_result_notes&xsec_token=AB15s...&xsec_source=pc_search
  likes: '1633'
  published_at: '2026-07-20'
  url: https://www.xiaohongshu.com/search_result/6a5e06bc000000001102f03c?xsec_token=ABoOKZF...&xsec_source=
```

---

### 2. `feed`（首页推荐流）
```bash
opencli xiaohongshu feed --limit 20 -f yaml
```
**实测返回结构**：
```yaml
- id: 6a8eee6c0000000026006458
  title: AI数据标注众包平台资讯
  type: normal   # normal: 图文笔记, video: 视频笔记
  author: 算了搞点钱
  likes: '11'
  url: https://www.xiaohongshu.com/explore/6a8eee6c0000000026006458?xsec_token=AB8o6s...&xsec_source=
```

---

### 3. `user`（博主主页作品）
```bash
opencli xiaohongshu user 5f310fd50000000001009df5 --limit 15 -f yaml
```
**实测返回结构**：
```yaml
- id: 69771bd900000000280239c3
  title: 强烈推荐，属于是玩嗨了
  type: normal
  likes: '2668'
  cover: http://sns-webpic-qc.xhscdn.com/202608280039/...!nc_n_webp_mw_1
  url: https://www.xiaohongshu.com/user/profile/5f310fd50000000001009df5/69771bd900000000280239c3?xsec_token=ABZ0j...&xsec_source=pc_user
```

---

### 4. `note`（读取单篇正文详情）
```bash
opencli xiaohongshu note "<带 xsec_token 的完整 URL>" -f yaml
```
**实测返回结构**：
```yaml
- field: title
  value: 企业刚需AI智能体Agent，全行业定制开发
- field: author
  value: 年客AI科技
- field: content
  value: >-
    如果说前几年大家还在惊叹大模型“聊得像人”，那么到了现在，企业老板们真正关心的核心已经变了：AI 能不能帮业务提效？...
- field: likes
  value: '11'
- field: collects
  value: '9'
- field: comments
  value: '2'
- field: tags
  value: '#AIAgent, #企业定制开发, #智能体, #年客AI'
```

---

### 5. `download`（多图与视频下载）
```bash
opencli xiaohongshu download "<带签名的 URL 或短链>" --output "./xhs_media" -f yaml
```
**实测返回结构（多图）**：
```yaml
Download complete: 4 downloaded
- index: 1
  type: image
  status: success
  size: 144.3 KB
- index: 2
  type: image
  status: success
  size: 175.8 KB
```
**实测返回结构（视频）**：
```yaml
Download complete: 2 downloaded
- index: 1
  type: video
  status: success
  size: 14.0 MB   # 原始 1080P/720P 高清 .mp4 视频
- index: 2
  type: image
  status: success
  size: 147.0 KB  # 视频封面大图
```

---

### 6. `comments`（评论树抓取）
```bash
opencli xiaohongshu comments "<带签名的 URL>" --with-replies -f yaml
```
**实测返回结构**：
```yaml
- rank: 1
  author: Lucy
  userId: 5ada30c211be1056fee8e4a6
  profileUrl: https://www.xiaohongshu.com/user/profile/5ada30c211be1056fee8e4a6
  text: 长期做有氧..就是发哥这种状态..看着不舒服
  likes: 16
  time: 08-13四川
  is_reply: false
  reply_to: ''
  images: []

- rank: 2
  author: '2223'
  userId: 65879451000000001c024d54
  profileUrl: https://www.xiaohongshu.com/user/profile/65879451000000001c024d54
  text: 有氧其实没坏处坏的是大量户外有氧，又晒太阳又跑三四个小时 不老才怪
  likes: 13
  time: 08-13英国
  is_reply: true
  reply_to: Lucy
  images: []
```
