# MySkill - 摸鱼办 Claude Code Skills

在 CSDN 极客日报和稀土掘金自动发布"摸鱼办"风格的早安评论/沸点。

配套 Claude Code 使用的 skill 插件，自动计算日期、距离周末/发薪日/节假日天数，生成温馨语录并发布。

## 包含的 Skills

| Skill | 平台 | 功能 | 触发词 |
|-------|------|------|--------|
| `csdn-comment` | CSDN | 在极客日报文章下发布摸鱼办评论 | "CSDN"、"csdn评论"、"摸鱼办" |
| `juejin-comment` | 稀土掘金 | 发布摸鱼办早安沸点 | "jj"、"掘金沸点"、"掘金摸鱼办" |

## 安装

### 方式一：直接克隆到 skills 目录

```bash
cd ~/.claude/skills
git clone https://github.com/Bhands6/MySkill.git
# 创建符号链接
ln -s MySkill/csdn-comment csdn-comment
ln -s MySkill/juejin-comment juejin-comment
```

### 方式二：手动复制

```bash
git clone https://github.com/Bhands6/MySkill.git
cp -r MySkill/csdn-comment ~/.claude/skills/
cp -r MySkill/juejin-comment ~/.claude/skills/
cp -r MySkill/shared ~/.claude/skills/
```

## 配置 Cookie

两个平台都需要浏览器登录 cookie 才能发布内容。

### CSDN Cookie

1. 在浏览器中登录 [CSDN](https://www.csdn.net/)
2. 按 `F12` 打开开发者工具 → `Application` → `Cookies`
3. 复制整个 cookie 字符串
4. 保存到文件：

```bash
echo "你的cookie内容" > ~/.csdn_cookie.txt
```

### 掘金 Cookie

1. 在浏览器中登录 [掘金](https://juejin.cn/)
2. 按 `F12` 打开开发者工具 → `Network` → 刷新页面 → 点击任意请求
3. 复制 Request Headers 中 `Cookie` 的完整值
4. 保存到文件：

```bash
echo "你的cookie内容" > ~/.juejin_cookie.txt
```

> Cookie 会过期，如果发布失败请重新获取。

## 使用方法

安装后在 Claude Code 中直接使用触发词即可：

```
> CSDN
> jj
> 发掘金沸点
> 摸鱼办
```

Claude 会自动完成：计算日期 → 生成语录和笑话 → 组装内容 → 发布。

## 直接使用脚本（不通过 Claude Code）

### 计算日期

```bash
# CSDN
python csdn-comment/scripts/csdn_comment.py --action dates

# 掘金
python juejin-comment/scripts/juejin_comment.py --action dates
```

### CSDN 查找文章

```bash
python csdn-comment/scripts/csdn_comment.py --action find_article \
  --cookie "$(cat ~/.csdn_cookie.txt)"
```

### CSDN 发布评论

```bash
python csdn-comment/scripts/csdn_comment.py --action post_comment \
  --cookie "$(cat ~/.csdn_cookie.txt)" \
  --article-id 123456789 \
  --content "评论内容"
```

### 掘金发布沸点

```bash
python juejin-comment/scripts/juejin_comment.py --action post_pin \
  --cookie "$(cat ~/.juejin_cookie.txt)" \
  --content "沸点内容" \
  --topic-id 6824710203301167112
```

### 掘金发布评论（API 方式）

```bash
python juejin-comment/scripts/juejin_comment.py --action post_comment \
  --cookie "$(cat ~/.juejin_cookie.txt)" \
  --article-id 7637734396590751750 \
  --content "评论内容"
```

### 掘金发布评论（Playwright 浏览器方式，需安装 playwright）

```bash
pip install playwright
playwright install chromium
python juejin-comment/scripts/juejin_playwright.py \
  --cookie-file ~/.juejin_cookie.txt \
  --pin-id 7637734396590751750 \
  --content "评论内容"
```

## 自定义

### 修改节假日

编辑 `shared/dates.py` 中的 `HOLIDAYS` 字典：

```python
HOLIDAYS = {
    "2026年端午节": "2026-06-19",
    "2026年中秋节": "2026-09-25",
    "2026年国庆节": "2026-10-01",
    # 添加更多...
}
```

### 修改发薪日

编辑 `shared/dates.py` 中的 `paydays` 列表：

```python
paydays = sorted(set([1, 5, 10, 15, 20, 25, last_day]))
```

## 项目结构

```
MySkill/
├── README.md
├── .gitignore
├── shared/
│   ├── __init__.py
│   └── dates.py              # 公共日期计算模块
├── csdn-comment/
│   ├── skill.md              # Claude Code skill 定义
│   └── scripts/
│       └── csdn_comment.py   # CSDN 工具脚本
└── juejin-comment/
    ├── skill.md              # Claude Code skill 定义
    └── scripts/
        ├── juejin_comment.py       # 掘金工具脚本
        └── juejin_playwright.py    # 掘金 Playwright 浏览器版
```

## 注意事项

- Cookie 等敏感信息不会被提交到仓库（已在 `.gitignore` 中排除）
- 节假日数据需要每年手动更新 `shared/dates.py`
- 掘金沸点发布后需要审核，不会立即显示
- Playwright 方式需要额外安装 `playwright` 和 `chromium`
