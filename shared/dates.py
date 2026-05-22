# -*- coding: utf-8 -*-
"""
摸鱼办公共日期计算模块
功能：计算距离周末、发薪日、节假日的天数，生成时段问候
"""

import json
import calendar
from datetime import datetime


# 节假日配置（每年需要更新）
# 格式: "显示名称": "YYYY-MM-DD"
HOLIDAYS = {
    "2026年端午节": "2026-06-19",
    "2026年中秋节": "2026-09-25",
    "2026年国庆节": "2026-10-01",
}

WEEKDAY_NAMES = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def calc_dates():
    """计算日期信息，返回 JSON 字符串"""
    now = datetime.now()
    today = now.date()
    weekday = today.weekday()  # 0=Monday

    # 距离周末
    days_to_sat = (5 - weekday) % 7
    if days_to_sat == 0 and now.hour >= 18:
        days_to_sat = 7
    days_to_sun = (days_to_sat + 1) % 7
    if days_to_sun == 0:
        days_to_sun = 7

    # 发薪日（1号到25号 + 本月最后一天）
    last_day = calendar.monthrange(today.year, today.month)[1]
    paydays = sorted(set([1, 5, 10, 15, 20, 25, last_day]))
    payday_lines = []
    for day in paydays:
        if day > today.day:
            target = today.replace(day=day)
        else:
            if today.month == 12:
                target = today.replace(year=today.year + 1, month=1, day=min(day, 31))
            else:
                next_month = today.month + 1
                next_last = calendar.monthrange(today.year, next_month)[1]
                target = today.replace(month=next_month, day=min(day, next_last))
        delta = (target - today).days
        if delta > 0:
            payday_lines.append(f"距离{day}号发薪日还有 ⏳ {delta} 天")

    # 节假日
    holiday_lines = []
    for name, date_str in HOLIDAYS.items():
        h_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        delta = (h_date - today).days
        if delta > 0:
            holiday_lines.append(f"距离{name}还有 ⏳ {delta} 天")

    # 时段问候
    hour = now.hour
    if 6 <= hour < 11:
        greeting = "早上好"
    elif 11 <= hour < 14:
        greeting = "中午好"
    elif 14 <= hour < 18:
        greeting = "下午好"
    elif 18 <= hour < 24:
        greeting = "晚上好"
    else:
        greeting = "夜深了"

    date_str = f"{today.year}年{today.month}月{today.day}号{WEEKDAY_NAMES[weekday]}"

    result = {
        "date_str": date_str,
        "weekday": WEEKDAY_NAMES[weekday],
        "greeting": greeting,
        "days_to_weekend_sat": days_to_sat,
        "days_to_weekend_sun": days_to_sun,
        "payday_lines": payday_lines,
        "holiday_lines": holiday_lines,
        "today": today.isoformat(),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)
