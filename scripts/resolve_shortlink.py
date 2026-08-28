# -*- coding: utf-8 -*-
"""
小红书移动端 302 分享短链自动解析中间件
支持 xhslink.cn / xhslink.com 短链自动跟随重定向并提取博主 ID / 笔记 ID / 完整签名长链
"""
import sys
import re
import json
import urllib.request

def resolve_xhs_url(short_url: str) -> dict:
    url_match = re.search(r'https?://[a-zA-Z0-9./\-_?=&#%]+', short_url.strip())
    target_url = url_match.group(0) if url_match else short_url.strip()
    
    req = urllib.request.Request(
        target_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        full_url = response.geturl()
    
    user_match = re.search(r'/user/profile/([0-9a-fA-F]{24})', full_url)
    note_match = re.search(r'/(?:explore|discovery/item|search_result|note)/([0-9a-fA-F]{24})', full_url)
    
    return {
        "short_url": target_url,
        "full_url": full_url,
        "user_id": user_match.group(1) if user_match else None,
        "note_id": note_match.group(1) if note_match else None,
        "type": "user" if user_match else ("note" if note_match else "unknown")
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python resolve_shortlink.py <xhs-short-url>")
        sys.exit(1)
    
    input_text = sys.argv[1]
    result = resolve_xhs_url(input_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
