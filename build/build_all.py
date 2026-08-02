# -*- coding: utf-8 -*-
"""ワンコマンド一括ビルド。fellows_db.json を直したら これ を実行するだけで
Obsidian金庫・wiki.html・index.html・Artifactソース の全てが再生成される。

  python build/build_all.py

そのあと 年表フォルダで:  git add -A && git commit -m "..." && git push
（Claude Artifact の更新は Claude 側で _artifact_source.html / _wiki_artifact.html を再Publish）
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
STEPS = ["build_vault.py", "build_wiki.py", "reinject_index.py", "make_artifact_sources.py"]

for s in STEPS:
    print(f"\n===> {s}")
    subprocess.run([PY, os.path.join(HERE, s)], check=True)

print("\n[OK] 全ビルド完了。次:  年表フォルダで  git add -A && git commit -m \"...\" && git push")
