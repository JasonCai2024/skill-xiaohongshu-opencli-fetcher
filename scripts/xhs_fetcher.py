# -*- coding: utf-8 -*-
"""
小红书 OpenCLI 全功能统一调用门面 (公开开源外壳)
核心引擎由 ServiceHub 加密核心模块 (_xhs_core) 驱动，仅限会员使用。
"""
import sys
import json
import argparse
import pathlib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except:
        pass

# 引入核心加密模块
current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))
try:
    from _xhs_core import OpenCLIDispatcher, ShortlinkResolver, ServiceHubAuth
except ImportError as e:
    print(f"❌ [错误] 核心加密模块加载失败: {e}\n👉 请确保 scripts/_xhs_core 目录完整。")
    sys.exit(1)

class XhsFetcher:
    @staticmethod
    def search(query: str, limit: int = 20, page: int = 1, sort: str = "general", all_results: bool = False):
        return OpenCLIDispatcher.search(query, limit=limit, page=page, sort=sort, all_results=all_results)

    @staticmethod
    def feed(limit: int = 20):
        return OpenCLIDispatcher.feed(limit)

    @staticmethod
    def user(user_id_or_url: str, limit: int = 15, all_results: bool = False):
        return OpenCLIDispatcher.user(user_id_or_url, limit=limit, all_results=all_results)

    @staticmethod
    def note(note_url_or_shortlink: str):
        return OpenCLIDispatcher.note(note_url_or_shortlink)

    @staticmethod
    def download(note_url_or_shortlink: str, output_dir: str = None):
        return OpenCLIDispatcher.download(note_url_or_shortlink, output_dir)

    @staticmethod
    def comments(note_url_or_shortlink: str, with_replies: bool = True, limit: int = 20):
        return OpenCLIDispatcher.comments(note_url_or_shortlink, with_replies=with_replies, limit=limit)

    @staticmethod
    def full_comments(note_url_or_shortlink: str, max_rounds: int = 40):
        return OpenCLIDispatcher.full_comments(note_url_or_shortlink, max_rounds)

    @staticmethod
    def resolve_shortlink(url_or_text: str):
        return ShortlinkResolver.resolve(url_or_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书数据抓取工具 (ServiceHub 会员专享)")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    p_search = subparsers.add_parser("search", help="关键词搜索")
    p_search.add_argument("query", help="搜索关键词")
    p_search.add_argument("--limit", type=int, default=20, help="返回条数 (默认 20)")
    p_search.add_argument("--page", type=int, default=1, help="翻页页码 (默认 1)")
    p_search.add_argument("--sort", default="general", help="排序方式 (general/latest/popularity)")
    p_search.add_argument("--all", dest="all_results", action="store_true", help="全量穷尽抓取所有笔记直至触底")

    p_feed = subparsers.add_parser("feed", help="首页推荐流")
    p_feed.add_argument("--limit", type=int, default=20, help="返回条数")

    p_user = subparsers.add_parser("user", help="博主作品")
    p_user.add_argument("target", help="博主 ID、主页 URL 或短链")
    p_user.add_argument("--limit", type=int, default=15, help="返回条数 (默认 15)")
    p_user.add_argument("--all", dest="all_results", action="store_true", help="全量穷尽抓取该博主的所有历史笔记直至触底")

    p_note = subparsers.add_parser("note", help="单篇笔记详情")
    p_note.add_argument("target", help="笔记 URL 或短链")

    p_download = subparsers.add_parser("download", help="下载多图或视频")
    p_download.add_argument("target", help="笔记 URL 或短链")
    p_download.add_argument("--output", help="输出目录")

    p_comments = subparsers.add_parser("comments", help="抓取评论")
    p_comments.add_argument("target", help="笔记 URL 或短链")
    p_comments.add_argument("--no-replies", action="store_true", help="不展开楼中楼")
    p_comments.add_argument("--limit", type=int, default=20, help="返回条数")

    p_full = subparsers.add_parser("full_comments", help="全量深度抓取评论")
    p_full.add_argument("target", help="笔记 URL 或短链")
    p_full.add_argument("--limit", type=int, default=500, help="采集深度")
    p_full.add_argument("-o", "--output", help="输出 JSON 文件路径")

    p_resolve = subparsers.add_parser("resolve", help="解析短链")
    p_resolve.add_argument("text", help="短链或包含短链的文案")

    args = parser.parse_args()

    fetcher = XhsFetcher()
    if args.command == "search":
        print(json.dumps(fetcher.search(args.query, limit=args.limit, page=args.page, sort=args.sort, all_results=args.all_results), ensure_ascii=False, indent=2))
    elif args.command == "feed":
        print(json.dumps(fetcher.feed(args.limit), ensure_ascii=False, indent=2))
    elif args.command == "user":
        print(json.dumps(fetcher.user(args.target, limit=args.limit, all_results=args.all_results), ensure_ascii=False, indent=2))
    elif args.command == "note":
        print(json.dumps(fetcher.note(args.target), ensure_ascii=False, indent=2))
    elif args.command == "download":
        print(json.dumps(fetcher.download(args.target, args.output), ensure_ascii=False, indent=2))
    elif args.command == "comments":
        print(json.dumps(fetcher.comments(args.target, not args.no_replies, args.limit), ensure_ascii=False, indent=2))
    elif args.command == "full_comments":
        data = fetcher.full_comments(args.target)
        if args.output:
            out_p = pathlib.Path(args.output).resolve()
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[+] 数据已保存至: {out_p}")
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.command == "resolve":
        print(json.dumps(fetcher.resolve_shortlink(args.text), ensure_ascii=False, indent=2))
    else:
        parser.print_help()
