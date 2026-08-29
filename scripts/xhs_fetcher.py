# -*- coding: utf-8 -*-
"""
OpenCLI 小红书全能力 Python 封装调用工具
提供结构化 JSON / Dict 返回，内置短链解析与命令编排
"""
import subprocess
import json
import shutil
import sys
from resolve_shortlink import resolve_xhs_url

class XhsFetcher:
    def __init__(self):
        if not shutil.which("opencli"):
            raise RuntimeError("未检测到 opencli 命令行工具，请先执行: npm install -g @jackwener/opencli")

    def _run_cmd(self, args: list) -> str:
        cmd = ["opencli", "xiaohongshu"] + args + ["-f", "json"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            raise RuntimeError(f"OpenCLI 命令执行失败: {res.stderr or res.stdout}")
        return res.stdout

    def doctor(self) -> str:
        res = subprocess.run(["opencli", "doctor"], capture_output=True, text=True, encoding="utf-8")
        return res.stdout

    def search(self, query: str, limit: int = 20):
        out = self._run_cmd(["search", query, "--limit", str(limit)])
        return json.loads(out)

    def feed(self, limit: int = 20):
        out = self._run_cmd(["feed", "--limit", str(limit)])
        return json.loads(out)

    def user(self, user_or_url: str, limit: int = 15):
        if "xhslink" in user_or_url:
            resolved = resolve_xhs_url(user_or_url)
            user_target = resolved["user_id"] or resolved["full_url"]
        else:
            user_target = user_or_url
        out = self._run_cmd(["user", user_target, "--limit", str(limit)])
        return json.loads(out)

    def note(self, note_or_url: str):
        if "xhslink" in note_or_url:
            resolved = resolve_xhs_url(note_or_url)
            note_url = resolved["full_url"]
        else:
            note_url = note_or_url
        out = self._run_cmd(["note", note_url])
        return json.loads(out)

    def download(self, note_or_url: str, output_dir: str = "./xhs_downloads"):
        if "xhslink" in note_or_url:
            resolved = resolve_xhs_url(note_or_url)
            target_url = resolved["full_url"]
        else:
            target_url = note_or_url
        cmd = ["opencli", "xiaohongshu", "download", target_url, "--output", output_dir, "-f", "json"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            raise RuntimeError(f"下载失败: {res.stderr or res.stdout}")
        return json.loads(res.stdout)

    def comments(self, note_or_url: str, with_replies: bool = True, limit: int = 50, use_mobile: bool = True):
        """
        获取单篇笔记评论树
        :param use_mobile: 默认 True。自动切换为 m.xiaohongshu.com 移动端模式，
                           可自动展开更多楼中楼子回复，将样本量从 18 条暴增至 75+ 条（提升 4 倍以上）
        """
        if "xhslink" in note_or_url:
            resolved = resolve_xhs_url(note_or_url)
            note_url = resolved["full_url"]
        else:
            note_url = note_or_url
            
        # 核心优化：自动切换为 m.xiaohongshu.com 以展开最多楼中楼
        if use_mobile and "www.xiaohongshu.com" in note_url:
            note_url = note_url.replace("www.xiaohongshu.com", "m.xiaohongshu.com")

        args = ["comments", note_url, "--limit", str(limit)]
        if with_replies:
            args.append("--with-replies")
        out = self._run_cmd(args)
        return json.loads(out)

if __name__ == "__main__":
    fetcher = XhsFetcher()
    print("OpenCLI 环境自检:")
    print(fetcher.doctor())
