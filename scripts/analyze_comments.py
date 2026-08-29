# -*- coding: utf-8 -*-
"""
小红书高价值评论自动化分析与全景报告生成器 (公开开源外壳)
核心分析逻辑由 ServiceHub 加密核心模块 (_xhs_core) 驱动，仅限会员使用。
"""
import sys
import os
import json
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
try:
    from _xhs_core import CommentAnalyzer, OpenCLIDispatcher
except ImportError as e:
    print(f"❌ [错误] 核心加密模块加载失败: {e}\n👉 请确保 scripts/_xhs_core 目录完整。")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书高价值评论自动化分析工具 (ServiceHub 会员专享)")
    parser.add_argument("input", help="已抓取的评论 JSON 文件路径，或者小红书笔记 URL / 移动端短链")
    parser.add_argument("--title", default="小红书爆款笔记", help="笔记标题 (可选)")
    parser.add_argument("--meta-total", type=int, default=0, help="官方元数据评论总数 (可选)")
    parser.add_argument("-o", "--output", help="输出 Markdown 报告文件路径 (可选)")

    args = parser.parse_args()

    inp = args.input.strip()
    if os.path.exists(inp) and inp.endswith(".json"):
        with open(inp, "r", encoding="utf-8") as f:
            data = json.load(f)
        comments = data.get("comments", []) if isinstance(data, dict) else data
    else:
        print(f"[*] 检测到输入为 URL，启动自动全量采集...")
        data = OpenCLIDispatcher.full_comments(inp)
        comments = data.get("comments", [])

    report = CommentAnalyzer.analyze(
        raw_comments=comments,
        note_title=args.title,
        meta_total=args.meta_total
    )

    if args.output:
        out_p = pathlib.Path(args.output).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(report, encoding="utf-8")
        print(f"[+] 分析报告已成功生成至: {out_p}")
    else:
        print("\n" + report)
