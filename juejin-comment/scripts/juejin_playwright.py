# -*- coding: utf-8 -*-
"""
掘金沸点评论 - Playwright 浏览器自动化版本
通过浏览器模拟发布评论，绕过 API 反爬虫保护
"""

import argparse
import json
import sys
from playwright.sync_api import sync_playwright


def post_comment(cookie_file: str, pin_id: str, content: str):
    """通过浏览器发布掘金评论"""
    # 读取 cookie
    with open(cookie_file, "r", encoding="utf-8") as f:
        cookie_str = f.read().strip()

    # 解析 cookie 字符串
    cookies = []
    for item in cookie_str.split("; "):
        if "=" in item:
            name, value = item.split("=", 1)
            cookies.append({
                "name": name,
                "value": value,
                "domain": ".juejin.cn",
                "path": "/",
            })

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # 添加 cookie
        context.add_cookies(cookies)

        page = context.new_page()

        try:
            # 导航到沸点页面
            url = f"https://juejin.cn/pin/{pin_id}"
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            # 找到评论输入框并点击
            comment_box = page.locator(".comment-box .reply-box-wrap textarea, .comment-box .reply-box-wrap [contenteditable]")
            if comment_box.count() > 0:
                comment_box.first.click()
                page.wait_for_timeout(500)

                # 输入评论内容
                comment_box.first.fill(content)
                page.wait_for_timeout(500)

                # 点击发布按钮
                submit_btn = page.locator(".comment-box .reply-box-wrap .submit-btn, .comment-box .reply-box-wrap button")
                if submit_btn.count() > 0:
                    submit_btn.first.click()
                    page.wait_for_timeout(3000)

                    print(json.dumps({
                        "success": True,
                        "message": "评论发布成功！",
                        "url": url,
                    }, ensure_ascii=False))
                else:
                    print(json.dumps({
                        "success": False,
                        "error": "未找到发布按钮",
                    }, ensure_ascii=False))
            else:
                # 尝试其他选择器
                page.screenshot(path="juejin_debug.png")
                print(json.dumps({
                    "success": False,
                    "error": "未找到评论输入框，已保存截图 juejin_debug.png",
                }, ensure_ascii=False))

        except Exception as e:
            page.screenshot(path="juejin_error.png")
            print(json.dumps({
                "success": False,
                "error": str(e),
                "screenshot": "juejin_error.png",
            }, ensure_ascii=False))
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="掘金沸点评论 - Playwright 版")
    parser.add_argument("--cookie-file", required=True, help="Cookie 文件路径")
    parser.add_argument("--pin-id", required=True, help="沸点 ID")
    parser.add_argument("--content", required=True, help="评论内容")

    args = parser.parse_args()
    post_comment(args.cookie_file, args.pin_id, args.content)


if __name__ == "__main__":
    main()
