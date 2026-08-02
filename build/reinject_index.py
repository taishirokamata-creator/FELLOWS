# -*- coding: utf-8 -*-
"""fellows_db.json と people_index.json を index.html の埋め込みデータへ再注入する。
build_vault.py（people_index.json 生成）→ このスクリプト の順で実行する。"""
import re, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))          # FELLOWS
NENPYO = os.path.join(BASE, "年表")

idx = os.path.join(NENPYO, "index.html")
html = open(idx, encoding="utf-8").read()
data = open(os.path.join(NENPYO, "data", "fellows_db.json"), encoding="utf-8").read().strip()
people = open(os.path.join(NENPYO, "data", "people_index.json"), encoding="utf-8").read().strip()

# const DATA = {...};  を丸ごと差し替え
html, n1 = re.subn(r'const DATA = \{[\s\S]*?\};', 'const DATA = ' + data + ';', html, count=1)
# const PEOPLE = __PEOPLE__;  または既注入の const PEOPLE = [...]; を差し替え
#   直後の行が「const esc」であることを手掛かりに終端を確定（誤マッチ防止）
html, n2 = re.subn(r'const PEOPLE = (?:__PEOPLE__|\[[\s\S]*?\]);(?=\r?\nconst esc)',
                   'const PEOPLE = ' + people + ';', html, count=1)

assert n1 == 1, "const DATA の差し替えに失敗（マーカーを確認）"
assert n2 == 1, "const PEOPLE の差し替えに失敗（マーカーを確認）"
open(idx, "w", encoding="utf-8").write(html)
print("index.html reinjected  (DATA + PEOPLE)")
