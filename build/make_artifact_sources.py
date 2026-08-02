# -*- coding: utf-8 -*-
"""index.html / wiki.html から Claude Artifact 用ソース（_artifact_source.html /
_wiki_artifact.html）を生成する。<!DOCTYPE>/<html>/<head>/<body> を除去し、
<style>〜</script> の中身だけを残す（Artifactは head/body を自動で付けるため）。"""
import re, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))
NENPYO = os.path.join(BASE, "年表")

def strip(src):
    s = open(src, encoding="utf-8").read()
    s = s[s.index("<style>"):]
    s = re.sub(r'</head>\s*<body[^>]*>', '\n', s, count=1)
    s = re.sub(r'</body>\s*</html>\s*$', '', s)
    return s.strip() + "\n"

open(os.path.join(NENPYO, "_artifact_source.html"), "w", encoding="utf-8").write(strip(os.path.join(NENPYO, "index.html")))
open(os.path.join(NENPYO, "_wiki_artifact.html"),  "w", encoding="utf-8").write(strip(os.path.join(NENPYO, "wiki.html")))
print("artifact sources regenerated  (_artifact_source.html / _wiki_artifact.html)")
