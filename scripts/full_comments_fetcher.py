# -*- coding: utf-8 -*-
"""
全量小红书评论抓取器（Full Comments Collector）
突破单次命令 50 条上限，通过平滑滚动触底 + 递归点击展开楼中楼子回复，
实现单篇笔记数百条全量评论的深度自动化采集与结构化去重。
"""
import sys
import os
import json
import time
import subprocess
import argparse
import pathlib

current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))
from resolve_shortlink import resolve_xhs_url

JS_COLLECTOR_TEMPLATE = """
(async () => {
    const wait = (ms) => new Promise(r => setTimeout(r, ms));
    const targetCount = __TARGET_COUNT__;
    const withReplies = __WITH_REPLIES__;
    
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

    const getScroller = () => {
        return document.querySelector('.note-scroller') 
            || document.querySelector('.interaction-container')
            || document.querySelector('.comments-container')
            || document.querySelector('.note-content')
            || document.documentElement;
    };

    const expandAllReplies = async () => {
        if (!withReplies) return 0;
        let clicked = 0;
        for (let round = 0; round < 4; round++) {
            const buttons = Array.from(document.querySelectorAll('button, [role="button"], span, div, a')).filter(el => {
                if (!(el instanceof HTMLElement)) return false;
                const t = (el.textContent || '').trim();
                if (!t || t.length > 25) return false;
                return /(展开|更多回复|全部回复|查看.*回复|共\\d+条回复)/.test(t) && !el.dataset.expandedClicked;
            });
            if (!buttons.length) break;
            for (const btn of buttons) {
                try {
                    btn.dataset.expandedClicked = "true";
                    btn.click();
                    clicked++;
                    await wait(200);
                } catch(e) {}
            }
            await wait(400);
        }
        return clicked;
    };

    let stallCount = 0;
    let lastCommentCount = 0;
    const maxRounds = 120;

    for (let round = 0; round < maxRounds; round++) {
        const scroller = getScroller();
        
        if (scroller) {
            scroller.scrollTop += 600;
            scroller.dispatchEvent(new Event('scroll', { bubbles: true }));
            scroller.dispatchEvent(new WheelEvent('wheel', { deltaY: 600, bubbles: true }));
        }

        const allComments = document.querySelectorAll('.parent-comment, .comment-item');
        if (allComments.length > 0) {
            const last = allComments[allComments.length - 1];
            if (typeof last.scrollIntoView === 'function') {
                last.scrollIntoView({ block: 'end', behavior: 'smooth' });
            }
        }

        await wait(600);
        await expandAllReplies();
        
        const currentCount = document.querySelectorAll('.parent-comment, .comment-item-sub, .sub-comment-item').length;
        
        if (currentCount >= targetCount) {
            break;
        }

        if (currentCount <= lastCommentCount) {
            stallCount++;
            if (stallCount >= 8) {
                break;
            }
        } else {
            stallCount = 0;
            lastCommentCount = currentCount;
        }
        
        await wait(600);
    }

    await expandAllReplies();
    await wait(800);

    const results = [];
    const seenIds = new Set();
    const clean = (el) => (el?.textContent || '').replace(/\\s+/g, ' ').trim();

    const parentNodes = document.querySelectorAll('.parent-comment');
    
    for (const p of parentNodes) {
        const rootItem = p.querySelector('.comment-item');
        if (!rootItem) continue;

        const authorEl = rootItem.querySelector('.author-wrapper .name, .user-name, .name');
        const author = clean(authorEl);
        const authorLink = rootItem.querySelector('a[href*="/user/profile/"]')?.getAttribute('href') || '';
        const userId = (authorLink.match(/\\/user\\/profile\\/([a-zA-Z0-9]+)/) || [])[1] || '';
        const profileUrl = userId ? `https://www.xiaohongshu.com/user/profile/${userId}` : '';
        const content = clean(rootItem.querySelector('.content, .note-text'));
        const likes = parseLikes(clean(rootItem.querySelector('.count, .like-wrapper .count')));
        const time = clean(rootItem.querySelector('.date, .time'));
        
        const images = [];
        rootItem.querySelectorAll('img').forEach(img => {
            if (img.classList.contains('avatar-item')) return;
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
        if (!seenIds.has(uniqueKey)) {
            seenIds.add(uniqueKey);
            results.push(rootCommentObj);
        }

        if (withReplies) {
            const subItems = p.querySelectorAll('.comment-item-sub, .sub-comment-list .comment-item, .reply-container .comment-item');
            for (const sub of subItems) {
                const sAuthorEl = sub.querySelector('.name, .user-name');
                const sAuthor = clean(sAuthorEl);
                const sAuthorLink = sub.querySelector('a[href*="/user/profile/"]')?.getAttribute('href') || '';
                const sUserId = (sAuthorLink.match(/\\/user\\/profile\\/([a-zA-Z0-9]+)/) || [])[1] || '';
                const sProfileUrl = sUserId ? `https://www.xiaohongshu.com/user/profile/${sUserId}` : '';
                const sContentEl = sub.querySelector('.content, .note-text');
                const sText = clean(sContentEl);
                const sLikes = parseLikes(clean(sub.querySelector('.count, .like-wrapper .count')));
                const sTime = clean(sub.querySelector('.date, .time'));
                const sReplyTo = clean(sContentEl?.querySelector(':scope > .nickname')) || author;
                
                const sImages = [];
                sub.querySelectorAll('img').forEach(img => {
                    if (img.classList.contains('avatar-item')) return;
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
                if (!seenIds.has(subUniqueKey)) {
                    seenIds.add(subUniqueKey);
                    results.push(subObj);
                }
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

def fetch_full_comments(note_url: str, max_comments: int = 500, with_replies: bool = True, session_name: str = "xhs-full-collector") -> dict:
    """
    全量抓取指定笔记的全部评论
    """
    if "xhslink" in note_url:
        resolved = resolve_xhs_url(note_url)
        target_url = resolved["full_url"]
    else:
        target_url = note_url.strip()

    # 优先使用移动端或桌面端标准长链
    if "www.xiaohongshu.com" in target_url:
        target_url = target_url.replace("www.xiaohongshu.com", "m.xiaohongshu.com")

    print(f"[*] 准备通过浏览器会话采集全量评论...")
    print(f"[*] 目标笔记 URL: {target_url}")
    print(f"[*] 目标采集上限: {max_comments} 条 | 楼中楼展开: {'开启' if with_replies else '关闭'}")

    open_cmd = ["opencli", "browser", session_name, "open", target_url]
    res = subprocess.run(open_cmd, capture_output=True, text=True, encoding="utf-8", shell=True)
    if res.returncode != 0:
        raise RuntimeError(f"打开浏览器页面失败: {res.stderr or res.stdout}")

    time.sleep(3)

    js_code = JS_COLLECTOR_TEMPLATE.replace("__TARGET_COUNT__", str(max_comments)).replace("__WITH_REPLIES__", "true" if with_replies else "false")
    single_line_js = " ".join(line.strip() for line in js_code.splitlines() if line.strip() and not line.strip().startswith("//"))
    
    print("[*] 正在执行智能增量滚动触底与楼中楼递归展开...")
    eval_cmd = ["opencli", "browser", session_name, "eval", single_line_js]
    eval_res = subprocess.run(eval_cmd, capture_output=True, text=True, encoding="utf-8", shell=True)
    
    if eval_res.returncode != 0:
        raise RuntimeError(f"评论采集执行异常: {eval_res.stderr or eval_res.stdout}")

    try:
        data = json.loads(eval_res.stdout)
    except Exception as e:
        raise RuntimeError(f"解析评论数据失败: {eval_res.stdout}") from e

    try:
        subprocess.run(["opencli", "browser", session_name, "close"], capture_output=True, shell=True)
    except:
        pass

    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书全量评论抓取增强工具")
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
    
    print(f"\n[+] 抓取完成！共获取 {result.get('total', 0)} 条评论（涵盖 {result.get('parentCount', 0)} 个一级主楼层）")
    
    if args.output:
        out_path = pathlib.Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[+] 数据已保存至: {out_path}")
    else:
        print("\n前 5 条评论预览:")
        print(json.dumps(result.get("comments", [])[:5], ensure_ascii=False, indent=2))
