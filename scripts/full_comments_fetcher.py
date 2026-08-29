# -*- coding: utf-8 -*-
"""
小红书全量评论深度抓取工具 (公开开源外壳)
由 ServiceHub 加密核心模块 (_xhs_core) 驱动。
"""
import sys
import json
import argparse
import pathlib

current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))
try:
    from _xhs_core import OpenCLIDispatcher
except ImportError as e:
    print(f"❌ [错误] 核心加密模块加载失败: {e}")
    sys.exit(1)

def fetch_full_comments(url_or_shortlink: str, max_rounds: int = 40):
    return OpenCLIDispatcher.full_comments(url_or_shortlink, max_rounds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书全量评论深度抓取工具 (ServiceHub 会员专享)")
    parser.add_argument("url", help="小红书笔记 URL 或移动端短链")
    parser.add_argument("--limit", type=int, default=500, help="采集深度")
    parser.add_argument("-o", "--output", help="输出 JSON 文件路径 (可选)")
    args = parser.parse_args()

    data = fetch_full_comments(args.url)
    if args.output:
        out_p = pathlib.Path(args.output).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[+] 数据已保存至: {out_p}")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
