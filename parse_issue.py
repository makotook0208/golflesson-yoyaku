#!/usr/bin/env python3
"""Issueフォーム本文(ISSUE_BODY)を解析し、DATE/SLOT1.. を GITHUB_ENV 形式で出力する。
Issueフォームは各項目を「### ラベル」+ 値 という形で本文に書き出す。
未入力は "_No response_"。"""
import os

body = os.environ.get("ISSUE_BODY", "")

sections = {}
cur, buf = None, []
for line in body.splitlines():
    if line.startswith("### "):
        if cur is not None:
            sections[cur] = "\n".join(buf).strip()
        cur, buf = line[4:].strip(), []
    else:
        buf.append(line)
if cur is not None:
    sections[cur] = "\n".join(buf).strip()


def val(keyword: str) -> str:
    for k, v in sections.items():
        if keyword in k:
            return "" if v == "_No response_" else v.strip()
    return ""


out = {
    "DATE": val("日付"),
    "SLOT1": val("①"),
    "SLOT2": val("②"),
    "SLOT3": val("③"),
    "NOTE": val("注記"),
}
for k, v in out.items():
    # 値は1行（ドロップダウン選択肢/短い日付）なのでそのまま KEY=VALUE で出力
    print(f"{k}={v}")
