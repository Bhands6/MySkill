# -*- coding: utf-8 -*-
"""
稀土掘金沸点工具
功能：计算日期、发布沸点、发布评论
"""

import argparse
import json
import sys
import os

# 将上级目录加入 path，以便引用 shared 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.dates import calc_dates as _calc_dates

import requests


# ==================== 日期计算 ====================

def calc_dates():
    """计算日期信息，输出 JSON"""
    print(_calc_dates())


# ==================== 发布沸点 ====================

def post_pin(cookie: str, content: str, topic_id: str = "0"):
    """发布掘金沸点"""
    url = "https://api.juejin.cn/content_api/v1/short_msg/publish"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": cookie,
        "Content-Type": "application/json",
        "Referer": "https://juejin.cn/",
        "Origin": "https://juejin.cn",
    }

    data = {
        "content": content,
        "pic_list": [],
        "topic_id": topic_id,
    }

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15, proxies={"http": None, "https": None})
        if resp.status_code == 200:
            try:
                result = resp.json()
                if result.get("err_no") == 0:
                    msg_id = result.get("data", {}).get("msg_id", "")
                    print(json.dumps({
                        "success": True,
                        "message": "沸点发布成功！",
                        "msg_id": msg_id,
                        "url": f"https://juejin.cn/pin/{msg_id}" if msg_id else "",
                    }, ensure_ascii=False))
                else:
                    print(json.dumps({
                        "success": False,
                        "message": result.get("err_msg", "发布失败"),
                        "err_no": result.get("err_no"),
                    }, ensure_ascii=False))
            except Exception:
                print(json.dumps({
                    "success": False,
                    "error": f"响应解析失败: {resp.text[:200]}",
                }, ensure_ascii=False))
        else:
            print(json.dumps({
                "success": False,
                "error": f"HTTP {resp.status_code}",
                "response": resp.text[:200],
            }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


# ==================== 发布评论 ====================

def post_comment(cookie: str, item_id: str, content: str):
    """发布掘金评论"""
    url = "https://api.juejin.cn/interact_api/v1/comment/publish"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": cookie,
        "Content-Type": "application/json",
        "Referer": f"https://juejin.cn/pin/{item_id}",
        "Origin": "https://juejin.cn",
    }

    data = {
        "comment_id": "0",
        "content": content,
        "item_id": item_id,
        "item_type": 4,
    }

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15, proxies={"http": None, "https": None})
        if resp.status_code == 200:
            # 掘金 publish 接口成功时返回空 body
            if len(resp.content) == 0 or resp.text.strip() == "":
                print(json.dumps({"success": True, "message": "评论发布成功！"}, ensure_ascii=False))
            else:
                try:
                    result = resp.json()
                    if result.get("err_no") == 0:
                        print(json.dumps({"success": True, "message": "评论发布成功！"}, ensure_ascii=False))
                    else:
                        print(json.dumps({
                            "success": False,
                            "message": result.get("err_msg", "发布失败"),
                            "err_no": result.get("err_no"),
                        }, ensure_ascii=False))
                except Exception:
                    print(json.dumps({
                        "success": False,
                        "error": f"响应解析失败: {resp.text[:200]}",
                    }, ensure_ascii=False))
        else:
            print(json.dumps({
                "success": False,
                "error": f"HTTP {resp.status_code}",
                "response": resp.text[:200],
            }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


# ==================== 主入口 ====================

def main():
    parser = argparse.ArgumentParser(description="掘金沸点工具")
    parser.add_argument("--action", required=True, choices=["dates", "post_pin", "post_comment"])
    parser.add_argument("--cookie", default="", help="掘金登录 cookie")
    parser.add_argument("--article-id", default="", help="沸点 ID（评论时使用）")
    parser.add_argument("--content", default="", help="内容")
    parser.add_argument("--topic-id", default="0", help="圈子/话题 ID（如上班摸鱼: 6824710203301167112）")

    args = parser.parse_args()

    if args.action == "dates":
        calc_dates()
    elif args.action == "post_pin":
        if not args.cookie:
            print(json.dumps({"error": "缺少 cookie 参数"}, ensure_ascii=False))
            sys.exit(1)
        if not args.content:
            print(json.dumps({"error": "缺少 content 参数"}, ensure_ascii=False))
            sys.exit(1)
        post_pin(args.cookie, args.content, args.topic_id)
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
