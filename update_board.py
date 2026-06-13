#!/usr/bin/env python3
"""予約状況ボード(index.html)を更新するスクリプト。
GitHub Actions の Run workflow フォーム、またはローカルから呼ばれる。
各値が空文字 / 「変更なし」のときは、その項目は今の値を維持する。
"""
import os
import re
import sys
from datetime import datetime, timezone, timedelta

HTML = os.path.join(os.path.dirname(__file__), "index.html")
KEEP = {"", "変更なし"}
JP_WD = ["月", "火", "水", "木", "金", "土", "日"]  # Monday=0


def set_slot(html: str, n: str, value: str) -> str:
    """data-slot="n" の枠の文字と色クラス(full/満員 / open/残り)を更新。"""
    if value in KEEP:
        return html
    cls = "full" if "満員" in value else "open"
    pattern = r'(<span class="status )(?:full|open)(" data-slot="%s">)[^<]*(</span>)' % re.escape(n)
    repl = r'\g<1>%s\g<2>%s\g<3>' % (cls, value)
    new, count = re.subn(pattern, repl, html)
    if count == 0:
        print(f"[warn] slot {n} not found", file=sys.stderr)
    return new


def set_date(html: str, value: str) -> str:
    """日付。"6/18" のような M/D を受け取り、(曜日)予約状況 を付けて整形。
    すでに（や予約状況を含む完全な文字列ならそのまま使う。"""
    if value in KEEP:
        return html
    text = value.strip()
    if "（" not in text and "予約状況" not in text:
        m = re.match(r'^\s*(\d{1,2})\s*/\s*(\d{1,2})\s*$', text)
        if m:
            month, day = int(m.group(1)), int(m.group(2))
            year = datetime.now(timezone(timedelta(hours=9))).year
            try:
                wd = JP_WD[datetime(year, month, day).weekday()]
                text = f"{month}/{day}（{wd}）予約状況"
            except ValueError:
                text = f"{month}/{day} 予約状況"
    pattern = r'(<p class="date" data-field="date">)[^<]*(</p>)'
    repl = r'\g<1>%s\g<2>' % text
    return re.subn(pattern, repl, html)[0]


def set_note(html: str, value: str) -> str:
    if value in KEEP:
        return html
    pattern = r'(<p class="note" data-field="note">)[^<]*(</p>)'
    return re.subn(pattern, r'\g<1>%s\g<2>' % value.strip(), html)[0]


def set_updated(html: str) -> str:
    now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y/%m/%d %H:%M")
    pattern = r'(<p class="updated">最終更新：)[^<]*(</p>)'
    return re.subn(pattern, r'\g<1>%s\g<2>' % now, html)[0]


def main():
    g = lambda k: os.environ.get(k, "")
    with open(HTML, encoding="utf-8") as f:
        html = f.read()
    html = set_date(html, g("DATE"))
    html = set_slot(html, "1", g("SLOT1"))
    html = set_slot(html, "2", g("SLOT2"))
    html = set_slot(html, "3", g("SLOT3"))
    html = set_note(html, g("NOTE"))
    html = set_updated(html)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("updated index.html")


if __name__ == "__main__":
    main()
