# -*- coding: utf-8 -*-
"""
移动端 302 短链自动解析中间件 (公开开源外壳)
由 ServiceHub 加密核心模块 (_xhs_core) 驱动。
"""
import sys
import json
import pathlib

current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))
try:
    from _xhs_core import ShortlinkResolver
except ImportError as e:
    print(f"❌ [错误] 核心加密模块加载失败: {e}")
    sys.exit(1)

def resolve_xhs_url(text: str):
    return ShortlinkResolver.resolve(text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python resolve_shortlink.py '<短链或分享文案>'")
        sys.exit(1)
    res = resolve_xhs_url(sys.argv[1])
    print(json.dumps(res, ensure_ascii=False, indent=2))
