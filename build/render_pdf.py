# -*- coding: utf-8 -*-
"""文字化けする（フォント埋め込みでテキスト層が壊れた）PDF台本を画像化する補助。
Claudeの Read はPDFのテキスト層を読むため、埋め込みフォントだと文字化けする。
その場合このスクリプトで各ページをPNG化すれば、Claudeが画像として正しく読める。

  python build/render_pdf.py "C:/path/to/台本.pdf" [dpi=150]

出力: 台本.pdf と同じ場所に 台本_img/p01.png, p02.png ... を作る。
依存: PyMuPDF （pip install pymupdf）
"""
import sys, os

def main():
    if len(sys.argv) < 2:
        print("usage: python render_pdf.py <pdf> [dpi]"); return
    import fitz  # PyMuPDF
    pdf = sys.argv[1]
    dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    out = os.path.splitext(pdf)[0] + "_img"
    os.makedirs(out, exist_ok=True)
    doc = fitz.open(pdf)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    for i, pg in enumerate(doc, 1):
        pg.get_pixmap(matrix=mat).save(os.path.join(out, f"p{i:02d}.png"))
    print(f"rendered {doc.page_count} pages -> {out}")

if __name__ == "__main__":
    main()
