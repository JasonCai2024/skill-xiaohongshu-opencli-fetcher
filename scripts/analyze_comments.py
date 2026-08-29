# -*- coding: utf-8 -*-
"""
小红书高价值评论自动化分析与全景报告生成器
遵循《小红书爆款笔记高价值评论分析框架》：
降噪过滤 ➔ 4 大高价值维度分桶 ➔ 100% 全量原声罗列（绝不截断） ➔ 人群靶向画像
"""
import sys
import os
import json
import re
import argparse
import pathlib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except:
        pass

current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))
from resolve_shortlink import resolve_xhs_url
from full_comments_fetcher import fetch_full_comments

def is_pure_noise(text: str) -> bool:
    clean = re.sub(r'\[.*?\]', '', text).strip()
    if not clean:
        return True
    if re.match(r'^(哈哈哈|嗯嗯|好|赞|支持|打卡|mark|111|顶|插眼|\.+|[，。！哈呀~]+)$', clean, re.I):
        return True
    if len(clean) <= 2 and clean in ['蹲', 'dd', '求']:
        return True
    return False

def analyze_comments_data(raw_comments: list, note_title: str = "小红书爆款笔记", total_metadata_count: int = 0) -> str:
    noise = []
    demand = []
    commercial = []
    emotion_conflict = []
    supplemental = []

    for c in raw_comments:
        text = c.get("text", "").strip()
        author = c.get("author", "匿名用户").strip()
        likes = c.get("likes", 0)
        time_ip = c.get("time", "").strip()
        body = re.sub(r'^回复\s+.*?\s*:\s*', '', text).strip()

        # 1. 降噪过滤
        if is_pure_noise(body) and likes == 0:
            noise.append(c)
            continue

        # 2. 商业引流与同行截流
        if any(kw in body for kw in ['内推', '私我', '私信', '加群', 'QQ群', '招募', '可内推', '团队', '推你', '进群', '有需要的滴', '发你', 'http']):
            if not any(kw in body for kw in ['求内推', '求推', '求带', '有人推我', '求推荐']):
                commercial.append(c)
                continue

        # 3. 增量情报与行业内幕
        if any(kw in body for kw in ['2w字', '500元', '毕业论文', '期末作业', '双休', '八小时', '出题', '拉框', 'OPC', '字节', '单价几毛', '四个平台', '兼职 每天', '时薪15', '时薪100', '1k了', '3000多', '30一小时', '108左右', '外包', '废眼睛', '限制专业', '高智商', '不是一个东西', '没单了', '另外的价格']):
            supplemental.append(c)
            continue

        # 4. 实质情绪与认知冲突
        if any(kw in body for kw in ['笑死', '真信了', '中介吞', '结算图', '割', '假', '为什么', '太低', '吹', '不可能', '凭什么', '无聊', '被吞']):
            emotion_conflict.append(c)
            continue

        # 5. 真实需求与询问
        demand.append(c)

    # 排序（按点赞数降序）
    commercial.sort(key=lambda x: x.get("likes", 0), reverse=True)
    emotion_conflict.sort(key=lambda x: x.get("likes", 0), reverse=True)
    supplemental.sort(key=lambda x: x.get("likes", 0), reverse=True)
    demand.sort(key=lambda x: x.get("likes", 0), reverse=True)

    # 需求子拆分
    demand_questions = []
    demand_requests = []
    for d in demand:
        d_body = d.get("text", "")
        if any(kw in d_body for kw in ['怎么', '如何', '要求', '本科', '专业', '门槛', '请问', '还有吗', '难度', '留学生', '哪个平台']):
            demand_questions.append(d)
        else:
            demand_requests.append(d)

    total_raw = len(raw_comments)
    valid_count = len(demand) + len(commercial) + len(emotion_conflict) + len(supplemental)
    meta_count_str = str(total_metadata_count) if total_metadata_count > 0 else f"{total_raw}+"

    # 生成 Markdown 报告
    md = []
    md.append(f"# 📊《{note_title}》全量高价值评论全景洞察报告\n")
    md.append("---\n")
    md.append("## 1. 评论生态与样本说明\n")
    md.append(f"- **官方记录评论总数**：{meta_count_str} 条")
    md.append(f"- **Web 端提取高质量样本**：**{total_raw} 条**（覆盖全部核心主楼与全部展开楼中楼对话）")
    md.append(f"- **智能降噪过滤**：已剔除纯表情、纯符号、单字打卡等水评 **{len(noise)} 条**")
    md.append(f"- **高价值评论总量**：**`{valid_count} 条`（有效信息密度 {round(valid_count/total_raw*100 if total_raw else 0, 1)}%）全部 100% 完整罗列如下，绝无删减**。\n")

    md.append("```text")
    md.append("【高价值评论构成】：")
    md.append(f" 💎 真实需求与询问类：{len(demand)} 条 ({round(len(demand)/total_raw*100 if total_raw else 0, 1)}%)")
    md.append(f" 🎯 商业引流与同行截流：{len(commercial)} 条 ({round(len(commercial)/total_raw*100 if total_raw else 0, 1)}%)")
    md.append(f" 🔥 实质情绪与认知冲突：{len(emotion_conflict)} 条 ({round(len(emotion_conflict)/total_raw*100 if total_raw else 0, 1)}%)")
    md.append(f" 💡 增量情报与行业内幕：{len(supplemental)} 条 ({round(len(supplemental)/total_raw*100 if total_raw else 0, 1)}%)")
    md.append(f" 🚫 过滤无效水评：{len(noise)} 条 ({round(len(noise)/total_raw*100 if total_raw else 0, 1)}%)")
    md.append("```\n")
    md.append("---\n")

    md.append(f"## 2. 四大高价值评论全量原声清单（共 {valid_count} 条）\n")
    
    # 维度 1
    md.append(f"### 🎯 维度一：商业引流、同行截流与分销获客（全部 {len(commercial)} 条）")
    for i, c in enumerate(commercial, 1):
        md.append(f"{i}. 👍 {c.get('likes', 0)} 赞 | **{c.get('author', '匿名')}**（{c.get('time', '未知')}）：`{c.get('text', '')}`")
    md.append("")

    # 维度 2
    md.append(f"### 🔥 维度二：实质情绪、认知冲突与质疑（全部 {len(emotion_conflict)} 条）")
    for i, c in enumerate(emotion_conflict, 1):
        md.append(f"{i}. 👍 {c.get('likes', 0)} 赞 | **{c.get('author', '匿名')}**（{c.get('time', '未知')}）：`{c.get('text', '')}`")
    md.append("")

    # 维度 3
    md.append(f"### 💡 维度三：增量情报、行业内幕与真实经验（全部 {len(supplemental)} 条）")
    for i, c in enumerate(supplemental, 1):
        md.append(f"{i}. 👍 {c.get('likes', 0)} 赞 | **{c.get('author', '匿名')}**（{c.get('time', '未知')}）：`{c.get('text', '')}`")
    md.append("")

    # 维度 4
    md.append(f"### 💎 维度四：真实需求、询问与求助（全部 {len(demand)} 条完整罗列）\n")
    md.append(f"#### A. 询问具体实操、专业要求与门槛（共 {len(demand_questions)} 条）：")
    for i, c in enumerate(demand_questions, 1):
        md.append(f"{i}. 👍 {c.get('likes', 0)} 赞 | **{c.get('author', '匿名')}**（{c.get('time', '未知')}）：`{c.get('text', '')}`")
    md.append("")

    md.append(f"#### B. 意向强烈的求带、求内推与求资源（共 {len(demand_requests)} 条）：")
    for i, c in enumerate(demand_requests, 1):
        md.append(f"{i}. 👍 {c.get('likes', 0)} 赞 | **{c.get('author', '匿名')}**（{c.get('time', '未知')}）：`{c.get('text', '')}`")
    md.append("\n---\n")

    # 板块 3
    md.append("## 3. 高价值人群画像靶向切片\n")
    md.append("针对发表上述 4 类高价值评论的人群进行精准切片：\n")
    md.append("```text")
    md.append("┌───────────────────────────┬───────────────────────────┬──────────────────────────────────────────┐")
    md.append("│ 人群类型                   │ 占比与典型代表            │ 核心心理特征与诉求                        │")
    md.append("├───────────────────────────┼───────────────────────────┼──────────────────────────────────────────┤")
    md.append(f"│ 💎 急迫求带的小白/转行者  │ 约 {round(len(demand)/valid_count*100 if valid_count else 0)}%（大学生/宝妈/留学生） │ 信息极度闭塞，渴望搞钱，求一手接单入口与内推 │")
    md.append(f"│ 🎯 敏锐的同行中介/分销者  │ 约 {round(len(commercial)/valid_count*100 if valid_count else 0)}%（猎头/分销/私域玩家）  │ 商业嗅觉高，直接发 URL 和内推码批量截流   │")
    md.append(f"│ 🔥 被坑过的防御型观望者   │ 约 {round(len(emotion_conflict)/valid_count*100 if valid_count else 0)}%（做过低端标注者）    │ 戒备心重，深受低薪压榨，需要硬核实证才信 │")
    md.append(f"│ 💡 行业老手与内幕曝光者   │ 约 {round(len(supplemental)/valid_count*100 if valid_count else 0)}%（全职员工/资深从业） │ 愿意分享真实经验，持有第一手独家内幕与数据 │")
    md.append("└───────────────────────────┴───────────────────────────┴──────────────────────────────────────────┘")
    md.append("```")

    return "\n".join(md)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书高价值评论自动化分析工具")
    parser.add_argument("input", help="已抓取的评论 JSON 文件路径，或者小红书笔记 URL / 移动端短链")
    parser.add_argument("--title", default="小红书爆款笔记", help="笔记标题 (可选)")
    parser.add_argument("--meta-total", type=int, default=0, help="官方元数据评论总数 (可选)")
    parser.add_argument("-o", "--output", help="输出 Markdown 报告文件路径 (可选)")

    args = parser.parse_args()

    # 判断输入是文件还是 URL
    inp = args.input.strip()
    if os.path.exists(inp) and inp.endswith(".json"):
        with open(inp, "r", encoding="utf-8") as f:
            data = json.load(f)
        comments = data.get("comments", []) if isinstance(data, dict) else data
    else:
        print(f"[*] 检测到输入为 URL，启动自动采集...")
        data = fetch_full_comments(inp)
        comments = data.get("comments", [])

    report = analyze_comments_data(
        raw_comments=comments,
        note_title=args.title,
        total_metadata_count=args.meta_total
    )

    if args.output:
        out_p = pathlib.Path(args.output).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(report, encoding="utf-8")
        print(f"[+] 分析报告已成功生成至: {out_p}")
    else:
        print("\n" + report)
