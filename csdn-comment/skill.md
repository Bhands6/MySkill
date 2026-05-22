---
name: csdn-comment
description: 在CSDN极客日报最新文章下发布摸鱼办早安评论。当用户说"CSDN"、"发CSDN评论"、"csdn评论"、"极客日报评论"、"摸鱼办"、"早安评论"时触发。自动计算日期、距离周末/发薪日/节假日的天数，生成温馨早安语录，找到极客日报最新文章并发布评论。
---

# CSDN 极客日报早安评论

在 CSDN 极客日报的最新文章下发布一条"摸鱼办"风格的早安评论。

## 前置条件

用户需要提供 CSDN 登录 cookie。首次使用时提示用户：

1. 在浏览器中登录 CSDN
2. 打开浏览器开发者工具 → Application → Cookies
3. 复制整个 cookie 字符串
4. 保存到 `~/.csdn_cookie.txt`

## 执行流程

### Step 1: 读取 Cookie

读取 `~/.csdn_cookie.txt` 获取 CSDN cookie。如果文件不存在，提示用户创建。

### Step 2: 计算日期信息

使用脚本计算：

```bash
py -3 <skill-path>/scripts/csdn_comment.py --action dates
```

输出 JSON 包含：
- `date_str`: 中文日期（如"2026年5月11号星期一"）
- `days_to_weekend_sat`: 距离周六天数
- `days_to_weekend_sun`: 距离周日天数
- `days_to_paydays`: 各发薪日剩余天数列表
- `days_to_holidays`: 各节假日剩余天数列表

### Step 3: 生成早安语录

根据当前日期和星期，生成一条温馨的早安语录。要求：
- 15-30字左右
- 温馨、积极、有趣
- 可以结合星期几的特点（如周一加油、周五期待周末等）
- 不要重复使用相同的语录

### Step 3.5: 生成笑话

生成一个简短的笑话或冷笑话。要求：
- 10-30字左右
- 适合程序员或上班族
- 轻松幽默，不要太冷
- 可以是编程梗、职场梗、生活梗等
- 每次不要重复

### Step 4: 组装评论内容

使用以下模板组装评论（注意 CSDN 评论支持 Markdown）：

```
各位C友们，{时段问候}！
今天{date_str}！
摸鱼办在此温馨提醒您：

🥳 周末
距离周末双休还有 ⏳ {days_to_weekend_sat} 天
距离周末单休还有 ⏳ {days_to_weekend_sun} 天

💴 工资
{payday_lines}

🎉 节假日
{holiday_lines}

摸鱼办温馨提示：
{语录}
{笑话}

——摸鱼办 敬上（用Claude code自动发布)
```

**时段问候规则：**
- 6:00-10:59 → "早上好"
- 11:00-13:59 → "中午好"
- 14:00-17:59 → "下午好"
- 18:00-23:59 → "晚上好"
- 0:00-5:59 → "夜深了"

其中 `payday_lines` 和 `holiday_lines` 根据实际天数动态生成，只包含未来日期。

### Step 5: 找到目标文章

**默认行为：自动从极客头条专栏获取**

脚本默认从 `csdngeeknews`（极客头条专栏，用户名 `weixin_39786569`）获取最新文章，无需用户手动指定：

```bash
py -3 <skill-path>/scripts/csdn_comment.py --action find_article --cookie "$(cat ~/.csdn_cookie.txt)"
```

脚本会自动尝试两个用户名（`csdngeeknews` 和 `weixin_39786569`），返回最新文章列表，选择第一篇即可。

**方式 A：用户直接提供文章链接**

如果用户提供了 CSDN 文章链接，直接提取 article_id：

```bash
py -3 <skill-path>/scripts/csdn_comment.py --action extract_id --url "<文章链接>"
```

**方式 B：指定其他用户名**

```bash
py -3 <skill-path>/scripts/csdn_comment.py --action find_article --cookie "$(cat ~/.csdn_cookie.txt)" --username <用户名>
```

### Step 6: 发布评论

```bash
py -3 <skill-path>/scripts/csdn_comment.py --action post_comment \
  --cookie "$(cat ~/.csdn_cookie.txt)" \
  --article-id <article_id> \
  --content "<评论内容>"
```

### Step 7: 确认结果

发布成功后告知用户：
- 文章标题和链接
- 评论内容预览
- 发布状态

## 注意事项

- 如果 cookie 过期，提示用户重新获取
- 评论内容中的 emoji 需要确保 CSDN 支持
- 发薪日和节假日只显示未来的（已过的不显示）
- 如果找不到极客日报文章，提示用户手动提供文章链接
