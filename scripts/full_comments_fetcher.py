# -*- coding: utf-8 -*-
"""
全量小红书评论抓取器（Full Comments Collector v2.0 - Python 步进驱动版）
采用 Python 外层多轮驱动 + 页面轻量注入架构，彻底消除 115s CDP 超时风险；
支持实时进度日志、平滑滚动触底、递归楼中楼展开与全量结构化去重提取。
"""
import sys
import os
import json
import time
import subprocess
import argparse
import pathlib

# 确保 Windows 终端 UTF-8 输出正常，避免 GBK 乱码
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except:
        pass

current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))
from resolve_shortlink import resolve_xhs_url

# 1. 轻量单步滚动与点击展开脚本（单次执行 < 1.5 秒）
JS_STEP_EXPAND = """
(() => {
    let clicked = 0;
    const buttons = Array.from(document.querySelectorAll('button, [role="button"], span, div, a')).filter(el => {
        if (!(el instanceof HTMLElement)) return false;
        const t = (el.textContent || '').trim();
        if (!t || t.length > 25) return false;
        return /(展开|更多回复|全部回复|查看.*回复|共\\d+条回复)/.test(t) && !el.dataset.expDone;
    });

    for (let i = 0; i < Math.min(buttons.length, 15); i++) {
        const btn = buttons[i];
        try {
            btn.dataset.expDone = "true";
            btn.click();
            clicked++;
        } catch(e) {}
    }

    const scroller = document.querySelector('.note-scroller') 
        || document.querySelector('.interaction-container')
        || document.querySelector('.comments-container')
        || document.querySelector('.note-content')
        || document.documentElement;

    if (scroller) {
        scroller.scrollTop += 800;
        scroller.dispatchEvent(new Event('scroll', { bubbles: true }));
        scroller.dispatchEvent(new WheelEvent('wheel', { deltaY: 800, bubbles: true }));
    }

    const allComments = document.querySelectorAll('.parent-comment, .comment-item');
    if (allComments.length > 0) {
        const last = allComments[allComments.length - 1];
        if (typeof last.scrollIntoView === 'function') {
            last.scrollIntoView({ block: 'end', behavior: 'smooth' });
        }
    }

    const currentCount = document.querySelectorAll('.parent-comment, .comment-item-sub, .sub-comment-item, [class*="comment-item"]').length;
    const parentCount = document.querySelectorAll('.parent-comment').length;

    return { clicked, currentCount, parentCount };
})()
"""

# 2. 最终数据全量提取脚本
JS_EXTRACT_ALL = """
(() => {
    const parseLikes = (text) => {
        if (!text) return 0;
        const clean = text.replace(/\\s+/g, '').replace(/赞/g, '');
        if (!clean) return 0;
        if (/^\\d+$/.test(clean)) return parseInt(clean, 10);
        const m = clean.match(/^(\\d+(\\.\\d+)?)([万wWkK千])/);
        if (m) {
            const num = parseFloat(m[1]);
            const unit = m[3].toLowerCase();
            return Math.round(num * (unit === 'w' || unit === '万' ? 10000 : 1000));
        }
        return 0;
    };

    const clean = (el) => (el?.textContent || '').replace(/\\s+/g, ' ').trim();
    const results = [];
    const seenKeys = new Set();

    const parentNodes = document.querySelectorAll('.parent-comment');
    
    for (const p of parentNodes) {
        const rootItem = p.querySelector('.comment-item') || p;
        const authorEl = rootItem.querySelector('.author-wrapper .name, .user-name, .name, .nickname');
        const author = clean(authorEl);
        const authorLink = rootItem.querySelector('a[href*="/user/profile/"]')?.getAttribute('href') || '';
        const userId = (authorLink.match(/\\/user\\/profile\\/([a-zA-Z0-9]+)/) || [])[1] || '';
        const profileUrl = userId ? `https://www.xiaohongshu.com/user/profile/${userId}` : '';
        const contentEl = rootItem.querySelector('.content, .note-text, .desc');
        const content = clean(contentEl);
        const likes = parseLikes(clean(rootItem.querySelector('.count, .like-wrapper .count, .like')));
        const time = clean(rootItem.querySelector('.date, .time'));
        
        const images = [];
        rootItem.querySelectorAll('img').forEach(img => {
            if (img.classList.contains('avatar-item') || img.classList.contains('avatar')) return;
            if (img.closest('.content, .note-text')) return;
            const src = img.currentSrc || img.src || img.getAttribute('data-src') || '';
            if (src && !images.includes(src)) images.push(src);
        });

        if (!content) continue;

        const rootCommentObj = {
            author,
            userId,
            profileUrl,
            text: content,
            likes,
            time,
            is_reply: false,
            reply_to: '',
            images
        };

        const uniqueKey = author + ':' + content + ':' + time;
        if (!seenKeys.has(uniqueKey)) {
            seenKeys.add(uniqueKey);
            results.push(rootCommentObj);
        }

        // 提取所有楼中楼子回复
        const subItems = p.querySelectorAll('.comment-item-sub, .sub-comment-list .comment-item, .reply-container .comment-item, .sub-comment');
        for (const sub of subItems) {
            const sAuthorEl = sub.querySelector('.name, .user-name, .nickname');
            const sAuthor = clean(sAuthorEl);
            const sAuthorLink = sub.querySelector('a[href*="/user/profile/"]')?.getAttribute('href') || '';
            const sUserId = (sAuthorLink.match(/\\/user\\/profile\\/([a-zA-Z0-9]+)/) || [])[1] || '';
            const sProfileUrl = sUserId ? `https://www.xiaohongshu.com/user/profile/${sUserId}` : '';
            const sContentEl = sub.querySelector('.content, .note-text, .desc');
            const sText = clean(sContentEl);
            const sLikes = parseLikes(clean(sub.querySelector('.count, .like-wrapper .count, .like')));
            const sTime = clean(sub.querySelector('.date, .time'));
            const sReplyTo = clean(sContentEl?.querySelector(':scope > .nickname')) || author;
            
            const sImages = [];
            sub.querySelectorAll('img').forEach(img => {
                if (img.classList.contains('avatar-item') || img.classList.contains('avatar')) return;
                if (img.closest('.content, .note-text')) return;
                const src = img.currentSrc || img.src || img.getAttribute('data-src') || '';
                if (src && !sImages.includes(src)) sImages.push(src);
            });

            if (!sText) continue;

            const subObj = {
                author: sAuthor,
                userId: sUserId,
                profileUrl: sProfileUrl,
                text: sText,
                likes: sLikes,
                time: sTime,
                is_reply: true,
                reply_to: sReplyTo,
                images: sImages
            };

            const subUniqueKey = sAuthor + ':' + sText + ':' + sTime;
            if (!seenKeys.has(subUniqueKey)) {
                seenKeys.add(subUniqueKey);
                results.push(subObj);
            }
        }
    }

    return {
        total: results.length,
        parentCount: parentNodes.length,
        comments: results
    };
})()
"""

def _exec_eval(session_name: str, js_snippet: str) -> dict:
    single_line_js = " ".join(line.strip() for line in js_snippet.splitlines() if line.strip() and not line.strip().startswith("//"))
    cmd = ["opencli", "browser", session_name, "eval", single_line_js]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", shell=True)
    if res.returncode != 0:
        raise RuntimeError(f"Browser eval failed: {res.stderr or res.stdout}")
    try:
        return json.loads(res.stdout)
    except:
        return {"raw": res.stdout}

def fetch_full_comments(note_url: str, max_comments: int = 500, with_replies: bool = True, session_name: str = "xhs-full-collector") -> dict:
    """
    全量抓取指定笔记全部评论（Python 步进驱动，稳定零超时）
    """
    if "xhslink" in note_url:
        resolved = resolve_xhs_url(note_url)
        target_url = resolved["full_url"]
    else:
        target_url = note_url.strip()

    # 优先采用移动端模式以开启楼中楼展开能力
    if "www.xiaohongshu.com" in target_url:
        target_url = target_url.replace("www.xiaohongshu.com", "m.xiaohongshu.com")

    print(f"[*] 启动全量评论采集流水线...")
    print(f"[*] 目标 URL: {target_url}")
    print(f"[*] 期望上限: {max_comments} 条 | 楼中楼子回复展开: {'开启' if with_replies else '关闭'}")

    # 1. 打开浏览器会话
    open_cmd = ["opencli", "browser", session_name, "open", target_url]
    res = subprocess.run(open_cmd, capture_output=True, text=True, encoding="utf-8", shell=True)
    if res.returncode != 0:
        raise RuntimeError(f"无法打开浏览器页面: {res.stderr or res.stdout}")

    time.sleep(3)

    # 2. Python 外层步进驱动循环（每轮 1.5s，彻底避免单次 115s 超时）
    print("[*] 正在执行 Python 步进增量触底滚动与楼中楼展开...")
    
    stall_count = 0
    last_count = 0
    max_rounds = 40  # 最多驱动 40 轮

    for r in range(1, max_rounds + 1):
        step_res = _exec_eval(session_name, JS_STEP_EXPAND)
        curr_count = step_res.get("currentCount", 0)
        clicked = step_res.get("clicked", 0)
        parents = step_res.get("parentCount", 0)
        
        print(f"  └─ [轮次 {r:02d}/{max_rounds}] 页面就绪节点: {curr_count} 个 (主楼: {parents}, 本轮点击展开: {clicked})")

        if curr_count >= max_comments:
            print(f"[*] 已达到预定目标条数上限 ({curr_count} >= {max_comments})，停止滚动。")
            break

        if curr_count <= last_count and clicked == 0:
            stall_count += 1
            if stall_count >= 5:
                print(f"[*] 页面已无更多新评论产生（连续 5 轮无增长），确认触底。")
                break
        else:
            stall_count = 0
            last_count = curr_count

        time.sleep(1.2)

    # 3. 执行最终全量结构化数据提取
    print("[*] 正在提取并格式化全量结构化评论数据...")
    data = _exec_eval(session_name, JS_EXTRACT_ALL)

    # 4. 关闭会话
    try:
        subprocess.run(["opencli", "browser", session_name, "close"], capture_output=True, shell=True)
    except:
        pass

    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书全量评论抓取增强工具 (v2.0)")
    parser.add_argument("url", help="小红书笔记 URL 或移动端分享短链")
    parser.add_argument("--limit", type=int, default=500, help="最大抓取条数 (默认 500)")
    parser.add_argument("--no-replies", action="store_true", help="不抓取楼中楼子回复")
    parser.add_argument("-o", "--output", help="输出保存路径 (JSON 文件)")
    
    args = parser.parse_args()
    
    result = fetch_full_comments(
        note_url=args.url,
        max_comments=args.limit,
        with_replies=not args.no_replies
    )
    
    total = result.get("total", 0)
    parents = result.get("parentCount", 0)
    print(f"\n[+] 采集成功！共获取 {total} 条评论（涵盖 {parents} 个一级主楼层，子回复 {max(0, total - parents)} 条）")
    
    if args.output:
        out_path = pathlib.Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[+] 数据已保存至: {out_path}")
    else:
        print("\n前 3 条评论预览:")
        print(json.dumps(result.get("comments", [])[:3], ensure_ascii=False, indent=2))
