# -*- coding: utf-8 -*-
"""
CSDN 极客日报早安评论工具
功能：计算日期、查找文章、发布评论
"""

import argparse
import json
import sys
import re
import os

# 将上级目录加入 path，以便引用 shared 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.dates import calc_dates as _calc_dates

import requests


# ==================== 日期计算 ====================

def calc_dates():
    """计算日期信息，输出 JSON"""
    print(_calc_dates())


# ==================== 查找文章 ====================

def find_article(cookie: str = "", username: str = ""):
    """查找 CSDN 极客头条最新文章

    优先通过博客 API 获取指定用户的文章，失败时回退到搜索 API。
    默认用户: csdngeeknews (极客头条专栏)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    all_results = []

    # 方式 A：通过博客 API 获取指定用户的文章（最可靠）
    blog_usernames = [username] if username else ["csdngeeknews", "weixin_39786569"]
    for uname in blog_usernames:
        api_url = (
            f"https://blog.csdn.net/community/home-api/v1/get-business-list"
            f"?page=1&size=10&businessType=blog&orderby=&noMore=false&username={uname}"
        )
        api_headers = {**headers, "Referer": f"https://blog.csdn.net/{uname}?type=blog"}
        if cookie:
            api_headers["Cookie"] = cookie
        try:
            resp = requests.get(api_url, headers=api_headers, timeout=15)
            data = resp.json()
            articles = data.get("data", {}).get("list", [])
            for a in articles:
                aid = str(a.get("articleId", ""))
                if aid and not any(r["article_id"] == aid for r in all_results):
                    all_results.append({
                        "article_id": aid,
                        "title": a.get("title", ""),
                        "url": a.get("url", ""),
                        "nickname": a.get("nickName", uname),
                    })
        except Exception:
            continue

    # 方式 B：如果博客 API 没结果，回退到搜索 API
    if not all_results:
        search_url = "https://so.csdn.net/api/v3/search"
        search_headers = {**headers, "Referer": "https://so.csdn.net/"}
        queries = ["极客日报", "CSDN日报 摸鱼", "CSDN 极客日报 早安"]
        for q in queries:
            params = {"q": q, "t": "blog", "p": 1, "s": "new", "tm": 0}
            try:
                resp = requests.get(search_url, params=params, headers=search_headers, timeout=15)
                data = resp.json()
                for r in data.get("result_vos", []):
                    article_id = r.get("id", "")
                    if article_id and not any(a["article_id"] == article_id for a in all_results):
                        all_results.append({
                            "article_id": article_id,
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "nickname": r.get("nickname", ""),
                        })
            except Exception:
                continue

    if not all_results:
        print(json.dumps({"error": "未找到极客日报文章，请手动提供文章链接"}, ensure_ascii=False))
        sys.exit(1)

    # 按 article_id 降序排列（ID 越大越新），置顶文章排到最后
    all_results.sort(key=lambda x: int(x["article_id"]), reverse=True)

    print(json.dumps({"articles": all_results[:10]}, ensure_ascii=False, indent=2))


# ==================== 发布评论 ====================

def extract_article_id(url: str):
    """从 CSDN 文章 URL 中提取 article_id"""
    # URL 格式: https://blog.csdn.net/xxx/article/details/123456789
    match = re.search(r'/article/details/(\d+)', url)
    if match:
        print(json.dumps({"article_id": match.group(1), "url": url}, ensure_ascii=False))
    else:
        print(json.dumps({"error": f"无法从 URL 中提取文章 ID: {url}"}, ensure_ascii=False))
        sys.exit(1)


def post_comment(cookie: str, article_id: str, content: str):
    """发布 CSDN 评论"""
    url = "https://blog.csdn.net/phoenix/web/v1/comment/submit"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": cookie,
        "Referer": f"https://blog.csdn.net/weixin_39786569/article/details/{article_id}",
        "Origin": "https://blog.csdn.net",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = {
        "commentId": "",
        "content": content,
        "articleId": article_id,
    }

    try:
        resp = requests.post(url, headers=headers, data=data, timeout=15)
        try:
            result = resp.json()
        except Exception:
            print(json.dumps({
                "success": False,
                "error": f"响应非JSON: {resp.text[:200]}",
                "status_code": resp.status_code,
            }, ensure_ascii=False))
            sys.exit(1)

        if result.get("code") == 200:
            print(json.dumps({"success": True, "message": "评论发布成功！"}, ensure_ascii=False))
        else:
            print(json.dumps({
                "success": False,
                "message": result.get("message", "发布失败"),
                "code": result.get("code"),
            }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


# ==================== 主入口 ====================

def main():
    parser = argparse.ArgumentParser(description="CSDN 极客日报早安评论工具")
    parser.add_argument("--action", required=True, choices=["dates", "find_article", "post_comment", "extract_id"])
    parser.add_argument("--cookie", default="", help="CSDN 登录 cookie")
    parser.add_argument("--article-id", default="", help="文章 ID")
    parser.add_argument("--url", default="", help="文章 URL")
    parser.add_argument("--content", default="", help="评论内容")
    parser.add_argument("--username", default="", help="博客用户名（默认 csdngeeknews）")

    args = parser.parse_args()

    if args.action == "dates":
        calc_dates()
    elif args.action == "extract_id":
        if not args.url:
            print(json.dumps({"error": "缺少 --url 参数"}, ensure_ascii=False))
            sys.exit(1)
        extract_article_id(args.url)
    elif args.action == "find_article":
        find_article(cookie=args.cookie, username=args.username)
    elif args.action == "post_comment":
        if not args.cookie:
            print(json.dumps({"error": "缺少 cookie 参数"}, ensure_ascii=False))
            sys.exit(1)
        if not args.article_id:
            print(json.dumps({"error": "缺少 article-id 参数"}, ensure_ascii=False))
            sys.exit(1)
        if not args.content:
            print(json.dumps({"error": "缺少 content 参数"}, ensure_ascii=False))
            sys.exit(1)
        post_comment(args.cookie, args.article_id, args.content)


if __name__ == "__main__":
    main()
