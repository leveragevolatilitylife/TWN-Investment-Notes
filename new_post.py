#!/usr/bin/env python3
"""
新增一篇投資筆記文章。

用法:
    python3 scripts/new_post.py

會依序詢問標題、摘要、標籤,然後:
1. 用 template.html 產生一個新的文章 HTML 檔(檔名 = 日期 + 標題轉成的 slug)
2. 自動在 posts.json 最前面加一筆對應資料
3. 印出接下來要做的 git 指令

執行完之後,打開新產生的 <slug>.html,把裡面的
[小標題一] / [CONTENT] 等內容換成正式的文章內文,存檔即可。

需要在這個 repo 的根目錄下執行(跟 index.html 同一層)。
"""

import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "template.html"
POSTS_JSON = ROOT / "posts.json"


def slugify(title: str, today: str) -> str:
    """把標題轉成適合當檔名的 slug:日期 + 英數字。"""
    ascii_only = "".join(
        c for c in unicodedata.normalize("NFKD", title) if not unicodedata.combining(c)
    )
    ascii_only = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_only).strip("-").lower()
    if not ascii_only:
        ascii_only = "post"
    return f"{today}-{ascii_only}"[:60]


def main():
    if not TEMPLATE.exists() or not POSTS_JSON.exists():
        sys.exit("找不到 template.html 或 posts.json,請確認在 repo 根目錄執行這個腳本。")

    title = input("文章標題: ").strip()
    if not title:
        sys.exit("標題不能空白。")
    summary = input("一到兩句話的摘要(會顯示在列表頁): ").strip()
    tags_raw = input("標籤(用逗號分隔,例如: 策略邏輯,回測): ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    today = date.today().isoformat()
    slug = slugify(title, today)
    out_path = ROOT / f"{slug}.html"

    if out_path.exists():
        sys.exit(f"檔案 {out_path.name} 已經存在,請換個標題或手動處理。")

    html = TEMPLATE.read_text(encoding="utf-8")
    # 拿掉範本開頭給人看的使用說明註解
    html = re.sub(
        r"\n<!-- =+\n\s*文章範本使用說明.*?=+ -->\n",
        "",
        html,
        flags=re.S,
    )
    html = html.replace("[TITLE]", title)
    html = html.replace("[DATE]", today)
    html = html.replace("[TAGS,以頓號分隔]", "、".join(tags) if tags else "未分類")
    html = html.replace(
        "[SUMMARY —— 一到兩句話的摘要,會顯示在列表頁的卡片上]",
        summary or "(尚未填寫摘要)",
    )
    html = html.replace('content="[SUMMARY]"', f'content="{summary}"')

    out_path.write_text(html, encoding="utf-8")

    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts.insert(0, {
        "slug": slug,
        "title": title,
        "date": today,
        "summary": summary,
        "tags": tags,
    })
    POSTS_JSON.write_text(
        json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print()
    print(f"已建立: {slug}.html")
    print("已更新: posts.json")
    print()
    print("接下來:")
    print(f"  1. 打開 {slug}.html,把內文換成正式文章")
    print("  2. 存檔後執行:")
    print(f"     git add {slug}.html posts.json")
    print(f'     git commit -m "新增文章: {title}"')
    print("     git push")


if __name__ == "__main__":
    main()
