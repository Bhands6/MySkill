---
name: juejin-comment
description: 在稀土掘金发布摸鱼办早安沸点。当用户说"jj"、"发掘金沸点"、"juejin沸点"、"掘金摸鱼办"、"掘金早安"时触发。自动计算日期、距离周末/发薪日/节假日的天数，生成温馨语录并发布沸点。
---

# 掘金摸鱼办沸点

在稀土掘金发布一条"摸鱼办"风格的早安沸点。

## 前置条件

用户需要提供掘金登录 cookie。首次使用时提示用户：

1. 在浏览器中登录掘金
2. 按 F12 → Network → 刷新页面 → 点任意请求
3. 复制 Request Headers 中 Cookie 的完整字符串
4. 保存到 `~/.juejin_cookie.txt`

## 执行流程

### Step 1: 读取 Cookie

读取 `~/.juejin_cookie.txt`。如果不存在，提示用户创建。

### Step 2: 计算日期信息

```bash
py -3 <skill-path>/scripts/juejin_comment.py --action dates
```

输出 JSON 包含：
- `date_str`: 中文日期
- `greeting`: 时段问候（早上好/中午好/下午好/晚上好/夜深了）
- `days_to_weekend_sat/sun`: 距离周末天数
- `payday_lines`: 发薪日列表（1-25号排序 + 月末）
- `holiday_lines`: 节假日列表

### Step 3: 生成语录

根据当前日期和星期，生成一条温馨语录。要求：
- 15-30字，温馨积极
- 结合星期特点
- 不要重复

### Step 3.5: 生成笑话

生成一个简短的笑话或冷笑话。要求：
- 10-30字左右
- 适合程序员或上班族
- 轻松幽默，不要太冷
- 可以是编程梗、职场梗、生活梗等
- 每次不要重复

### Step 4: 组装沸点内容

```
各位J友们，{时段问候}！
今天{date_str}！
摸鱼办在此温馨提醒您：

🥳 周末
距离周末双休还有 ⏳ {days_to_weekend_sat}天
距离周末单休还有 ⏳ {days_to_weekend_sun}天

💴 工资
{payday_lines}

🎉 节假日
{holiday_lines}

摸鱼办温馨提示：
{语录}
{笑话}

——摸鱼办 敬上（用Claude code自动发布）
```

### Step 5: 发布沸点

```bash
py -3 <skill-path>/scripts/juejin_comment.py --action post_pin \
  --cookie "$(cat ~/.juejin_cookie.txt)" \
  --content "<沸点内容>" \
  --topic-id 6824710203301167112
```

圈子/话题 ID：
- `6824710203301167112` = 上班摸鱼
- `0` = 不指定圈子

### Step 6: 确认结果

发布成功后告知用户沸点链接和内容预览。

## 备用功能：发布评论

如需在已有沸点下发布评论：

```bash
py -3 <skill-path>/scripts/juejin_comment.py --action post_comment \
  --cookie "$(cat ~/.juejin_cookie.txt)" \
  --article-id <沸点ID> \
  --content "<评论内容>"
```

沸点 ID 从 URL 中提取，如 `https://juejin.cn/pin/7637734396590751750` → ID 为 `7637734396590751750`。

## 备用功能：Playwright 浏览器自动化

当 API 方式失败时，可使用 Playwright 浏览器自动化方式发布评论（需安装 playwright）：

```bash
py -3 <skill-path>/scripts/juejin_playwright.py \
  --cookie-file ~/.juejin_cookie.txt \
  --pin-id <沸点ID> \
  --content "<评论内容>"
```

## 注意事项

- 如果 cookie 过期，提示用户重新获取
- 发薪日和节假日只显示未来的（已过的不显示）
- 沸点发布后需要审核，不会立即显示
