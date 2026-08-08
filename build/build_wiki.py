# -*- coding: utf-8 -*-
"""Obsidian金庫 (FELLOWS_Vault) -> Wikipedia風 単一HTML (wiki.html)"""
import os, re, json, html as htmlmod

# パス可搬化：<FELLOWS>/年表/build/ に置く前提。BASE = FELLOWS（buildの2つ上）。
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))
VAULT = os.path.join(BASE, "FELLOWS_Vault")
OUT   = os.path.join(BASE, "年表", "wiki.html")

CAT_ORDER = ["年表", "公演", "天下一武狼会シリーズ", "キャラクター", "用語集"]
CAT_ICON  = {"年表":"🗺","公演":"📖","天下一武狼会シリーズ":"🏆","キャラクター":"👥","用語集":"📚","HOME":"🏠"}

def esc(s): return htmlmod.escape(s, quote=False)

# ---- 収集 ----
pages = {}   # title -> {title, cat, fm, raw}
def add_file(path, cat):
    with open(path, encoding="utf-8") as f: txt = f.read()
    title = os.path.splitext(os.path.basename(path))[0]
    fm = {}
    m = re.match(r'^---\n(.*?)\n---\n', txt, re.S)
    body = txt
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); fm[k.strip()] = v.strip()
        body = txt[m.end():]
    pages[title] = {"title": title, "cat": cat, "fm": fm, "raw": body}

for cat in os.listdir(VAULT):
    p = os.path.join(VAULT, cat)
    if os.path.isdir(p):
        for fn in os.listdir(p):
            if fn.endswith(".md"): add_file(os.path.join(p, fn), cat)
home_path = os.path.join(VAULT, "00_HOME.md")
if os.path.exists(home_path): add_file(home_path, "HOME")

titles = set(pages.keys())

# ---- リンク抽出 & backlink ----
LINK = re.compile(r'\[\[([^\]]+)\]\]')
for t, pg in pages.items():
    outs = []
    for m in LINK.finditer(pg["raw"]):
        tgt = m.group(1).split("|")[0].strip()
        if tgt in titles and tgt != t and tgt not in outs:
            outs.append(tgt)
    pg["links"] = outs
backlinks = {t: [] for t in pages}
for t, pg in pages.items():
    for o in pg["links"]:
        if t not in backlinks[o]:
            backlinks[o].append(t)

# ---- Markdown -> HTML（軽量） ----
def inline(s):
    s = esc(s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    def link(m):
        raw = m.group(1); tgt = raw.split("|")[0].strip(); label = raw.split("|")[-1].strip()
        if tgt in titles:
            return f'<a href="#{tgt}" class="wl">{esc(label)}</a>'
        return f'<span class="wl dead">{esc(label)}</span>'
    s = re.sub(r'\[\[([^\]]+)\]\]', link, s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    # 生URL（http/https）を外部リンク化（参考リンク用）
    s = re.sub(r'(?<!["\'>])(https?://[^\s、。」）)＞<]+)',
               r'<a href="\1" target="_blank" rel="noopener">\1</a>', s)
    return s

def md2html(body):
    out, ul, tbl = [], False, False
    def close_ul():
        nonlocal ul
        if ul: out.append("</ul>"); ul = False
    def close_tbl():
        nonlocal tbl
        if tbl: out.append("</tbody></table></div>"); tbl = False
    for line in body.splitlines():
        l = line.rstrip()
        if not l.strip():
            close_ul(); close_tbl(); continue
        if l.startswith("# "):
            close_ul(); close_tbl(); continue  # タイトルは別表示
        if l.startswith("### "):
            close_ul(); close_tbl(); out.append(f"<h4>{inline(l[4:])}</h4>"); continue
        if l.startswith("## "):
            close_ul(); close_tbl(); out.append(f"<h3>{inline(l[3:])}</h3>"); continue
        if l.startswith("> [!quote]"):
            close_ul(); close_tbl(); out.append(f'<blockquote>{inline(l.split("]",1)[1].strip())}</blockquote>'); continue
        if l.startswith(">"):
            close_ul(); close_tbl(); out.append(f'<blockquote>{inline(l[1:].strip())}</blockquote>'); continue
        if l.startswith("| "):
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):  # 区切り
                continue
            if not tbl:
                close_ul(); out.append('<div class="tw"><table><tbody>'); tbl = True
            out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if l.startswith("- ") or l.startswith("- [ ] "):
            close_tbl()
            if not ul: out.append("<ul>"); ul = True
            item = l[2:]
            if item.startswith("[ ] "): item = "☐ " + item[4:]
            out.append(f"<li>{inline(item)}</li>"); continue
        if set(l.strip()) <= set("-—─"):
            close_ul(); close_tbl(); out.append("<hr>"); continue
        close_ul(); close_tbl(); out.append(f"<p>{inline(l)}</p>")
    close_ul(); close_tbl()
    return "\n".join(out)

# ---- ページデータ生成 ----
FM_LABEL = {"type":"種別","区分":"区分","シリーズ":"シリーズ","現実開催日":"現実の開催日","作中年代":"作中年代","世代":"世代","tags":"タグ"}
data = {}
for t, pg in pages.items():
    fm = pg["fm"]
    infobox = []
    for k in ["type","区分","世代","シリーズ","現実開催日","作中年代","tags"]:
        if k in fm and fm[k] and k != "aliases":
            v = fm[k].strip('[]"').replace('"','').replace(", "," / ")
            infobox.append([FM_LABEL.get(k,k), v])
    data[t] = {
        "t": t, "cat": pg["cat"], "type": fm.get("type", pg["cat"]),
        "info": infobox, "html": md2html(pg["raw"]),
        "links": pg["links"], "back": backlinks[t],
    }

# ---- 目次: 五十音（ア行/カ行…）＋A–Z＋数字＋その他 でグループ化 ----
# 漢字・記号始まりの項目は読みを与える（未登録は自動判定＝先頭文字で分類）
YOMI = {
 # 公演
 "天下一武狼会シリーズ":"てんかいちぶろうかいしりーず","失われた天下一武狼会 第4回の記憶":"うしなわれたてんかいちぶろうかい",
 "怪獣":"かいじゅう","現代版天下一武狼会":"げんだいばんてんかいちぶろうかい",
 "銀河鉄道の夜 赤":"ぎんがてつどうのよるあか","銀河鉄道の夜 青":"ぎんがてつどうのよるあお",
 # 人物
 "三田村以外の新入生ほか":"みたむらいがいのしんにゅうせい","三田村（ミコ）":"みたむら","中島":"なかじま","中田":"なかた",
 "亜理紗は大変なものを盗んでいきました":"ありさはたいへんなものをぬすんでいきました","人狼ルームGM・レジェンド勢":"じんろうるーむじーえむ",
 "伊藤":"いとう","大野":"おおの","家政婦の・ミタ":"かせいふのみた","最長老":"さいちょうろう",
 "月の狼男（ストレンジディックス）":"つきのおおかみおとこ","村中":"むらなか","森本":"もりもと","真由美":"まゆみ",
 "結":"ゆい","脇脇脇男":"わきわきわきお","藤澤":"ふじさわ","蛍原徹":"けいばらとおる","阿部洸希":"あべこうき",
 "音楽と政治、両方尊重♥":"おんがくとせいじりょうほうそんちょう","香川":"かがわ",
 "魔理沙は大変なものを盗んでいきました":"まりさはたいへんなものをぬすんでいきました","（FELLOWS一同）":"ふぇろーずいちどう",
 # キーワード
 "「君の魔法」":"きみのまほう","人造人間（にゃんぽ子／ドクターペロ）":"じんぞうにんげん","占いジジ":"うらないじじ",
 "天下一武狼会／MTF・SMTF":"てんかいちぶろうかい","悪いAI（宇宙外生命体）":"わるいえーあい",
 "感情検閲AI「IJ」／イジュニア":"かんじょうけんえつ","改名メタ（2024年3月〜）（用語）":"かいめいめた",
 "阿部仲田クラス":"あべなかたくらす","青森／ハピゲ":"あおもり",
 # 設定
 "人狼ルーム":"じんろうるーむ","合言葉「We are FELLOWS!!」":"あいことば","悪いAI地球襲来事変（2043年）":"わるいえーあいちきゅう",
 "改名メタ（2024年3月〜）":"かいめいめた","青森 ・ ハピゲ":"あおもり",
 # 年表
 "正史年表":"せいしねんぴょう","現実の開催史":"げんじつのかいさいし","調べるリスト":"しらべるりすと",
}
_ROWS = {
 "ア行":"あいうえおぁぃぅぇぉゔ","カ行":"かきくけこがぎぐげごゕゖ","サ行":"さしすせそざじずぜぞ",
 "タ行":"たちつてとだぢづでどっ","ナ行":"なにぬねの","ハ行":"はひふへほばびぶべぼぱぴぷぺぽ",
 "マ行":"まみむめも","ヤ行":"やゆよゃゅょ","ラ行":"らりるれろ","ワ行":"わをんゎ",
}
CHAR2ROW = {ch: row for row, chars in _ROWS.items() for ch in chars}
GROUP_ORDER = ["ア行","カ行","サ行","タ行","ナ行","ハ行","マ行","ヤ行","ラ行","ワ行","A–Z","数字","その他"]
_STRIP = "「『（(【［〔｛{“”\"'’ 　・-—ー～"
def to_hira(s):
    out = []
    for ch in s:
        o = ord(ch)
        out.append(chr(o - 0x60) if 0x30A1 <= o <= 0x30F6 else ch)
    return "".join(out)
def reading(title):
    return to_hira(YOMI.get(title, title))
def group_of(title):
    r = reading(title).lstrip(_STRIP)
    c = r[:1]
    if c in CHAR2ROW: return CHAR2ROW[c]
    if c and (("a" <= c.lower() <= "z")): return "A–Z"
    if c and c.isdigit(): return "数字"
    return "その他"
def sortkey(title):
    g = group_of(title)
    return (GROUP_ORDER.index(g), reading(title).lstrip(_STRIP).lower(), title)

GROUP_MIN = 8  # これ未満のカテゴリは五十音で分けず素の一覧にする
index = {}
for c in CAT_ORDER + ["HOME"]:
    if c == "天下一武狼会シリーズ":
        # 五十音でばらさず、まとめ→小区分（FELLOWS学園主催／現代版／その他）→開催日順
        def _dk(t):
            m = re.search(r'(\d{4})年(\d{1,2})?月?(\d{1,2})?', pages[t]["fm"].get("現実開催日", ""))
            return (int(m.group(1)), int(m.group(2) or 99), int(m.group(3) or 99)) if m else (9999, 99, 99)
        allt = [t for t in data if data[t]["cat"] == c]
        matome = [t for t in allt if "目次" in pages[t]["fm"].get("type", "")]
        grp = [["", matome]] if matome else []
        for b in ["FELLOWS学園主催", "現代版", "その他"]:
            g = sorted([t for t in allt if pages[t]["fm"].get("区分", "") == b], key=_dk)
            if g: grp.append([b, g])
        index[c] = grp
        continue
    ts = sorted([t for t in data if data[t]["cat"] == c], key=sortkey)
    if c == "HOME" or len(ts) < GROUP_MIN:
        index[c] = [["", ts]]
    else:
        groups = {}
        for t in ts:
            groups.setdefault(group_of(t), []).append(t)
        index[c] = [[g, groups[g]] for g in GROUP_ORDER if g in groups]

payload = json.dumps({"pages": data, "index": index, "order": CAT_ORDER,
                      "icons": CAT_ICON}, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FELLOWS Wiki</title>
<style>
:root{--bg:#0d1117;--panel:#161b22;--panel2:#1c2330;--line:#2a3340;--text:#e6edf3;
 --muted:#9aa7b4;--accent:#e5484d;--link:#4aa3ff;--gold:#e3b341;--purple:#a071ff;--green:#3fb950}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
 font-family:"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,system-ui,sans-serif;line-height:1.7}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:10;display:flex;gap:14px;align-items:center;
 padding:12px 18px;background:rgba(13,17,23,.95);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
header .logo{font-weight:800;letter-spacing:.03em;white-space:nowrap}
header .logo b{color:var(--accent)}
#q{flex:1;max-width:520px;padding:9px 14px;border-radius:999px;border:1px solid var(--line);
 background:var(--panel);color:var(--text);font-size:14px}
#q:focus{outline:none;border-color:var(--accent)}
.wrap{display:grid;grid-template-columns:260px 1fr;gap:0;min-height:calc(100vh - 58px)}
#side{border-right:1px solid var(--line);padding:14px 10px;overflow:auto;max-height:calc(100vh - 58px);position:sticky;top:58px}
#side h4{margin:14px 8px 6px;font-size:12px;color:var(--muted);letter-spacing:.05em}
#side .grp{margin:6px 6px 1px;padding:3px 6px;border-radius:6px;font-size:12px;color:var(--purple);
 letter-spacing:.06em;font-weight:700;cursor:pointer;user-select:none;display:flex;align-items:center;gap:6px}
#side .grp:hover{background:var(--panel2)}
#side .grp .tw{font-size:9px;color:var(--muted);width:8px;flex:none;transition:transform .1s}
#side .grp .gn{margin-left:auto;font-size:10px;color:var(--muted);font-weight:400;opacity:.75}
#side .grpwrap{margin-left:4px;border-left:1px solid var(--line);padding-left:2px}
#side a{display:block;padding:4px 8px;border-radius:6px;color:var(--text);font-size:13px}
#side a:hover{background:var(--panel);text-decoration:none}
#side a.on{background:var(--accent);color:#fff}
main{padding:26px 34px 80px;max-width:900px}
.crumb{color:var(--muted);font-size:12px;margin-bottom:6px}
.badge{display:inline-block;font-size:11px;padding:2px 9px;border-radius:999px;background:var(--panel2);border:1px solid var(--line);color:var(--muted);margin-left:8px}
h1.pt{margin:.1em 0 .4em;font-size:28px;border-bottom:2px solid var(--accent);padding-bottom:.25em}
.infobox{float:right;width:270px;margin:0 0 16px 20px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:13px}
.infobox table{width:100%;border-collapse:collapse}
.infobox td{padding:4px 2px;vertical-align:top;border-bottom:1px solid var(--line)}
.infobox td:first-child{color:var(--muted);white-space:nowrap;width:34%}
.art h3{font-size:18px;margin:20px 0 6px;border-left:4px solid var(--accent);padding-left:10px}
.art h4{font-size:15px;margin:14px 0 4px;color:var(--gold)}
.art p{margin:8px 0}
.art ul{margin:6px 0 6px 4px;padding-left:20px}
.art li{margin:2px 0}
.art blockquote{margin:10px 0;padding:8px 14px;border-left:3px solid var(--link);background:var(--panel);border-radius:0 8px 8px 0;color:#d0d8e0}
.art hr{border:none;border-top:1px dashed var(--line);margin:14px 0}
.art code{background:var(--panel2);padding:1px 6px;border-radius:5px;font-size:.9em}
.tw{overflow-x:auto;margin:10px 0}
.art table{border-collapse:collapse;width:100%;font-size:13px}
.art td{border:1px solid var(--line);padding:6px 9px}
.wl{color:var(--link)}
.wl.dead{color:var(--muted);border-bottom:1px dotted var(--muted)}
.rel{margin-top:28px;border-top:1px solid var(--line);padding-top:14px}
.rel h3{font-size:14px;color:var(--muted);border:none;padding:0;margin:0 0 8px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chips a{font-size:12px;padding:3px 10px;border:1px solid var(--line);border-radius:999px;background:var(--panel)}
footer{color:var(--muted);font-size:12px;padding:16px 34px;border-top:1px solid var(--line)}
#menu{display:none}
@media(max-width:820px){
 .wrap{grid-template-columns:1fr}
 #menu{display:inline-block;background:var(--panel);border:1px solid var(--line);color:var(--text);
   border-radius:8px;padding:7px 10px;font-size:14px;cursor:pointer;white-space:nowrap;line-height:1}
 #side{display:none}
 body.nav-open #side{display:block;position:fixed;top:57px;left:0;right:0;bottom:0;z-index:40;
   background:var(--bg);max-height:none;overflow:auto;padding:14px;border:none}
 .infobox{float:none;width:auto;margin:0 0 16px}
 main{padding:18px}
}
</style></head><body>
<header>
 <button id="menu" aria-label="目次を開閉">☰ 目次</button>
 <div class="logo">🐺 <b>FELLOWS</b> Wiki</div>
 <input id="q" placeholder="検索（公演・人物・キーワード…）" autocomplete="off">
 <a href="#00_HOME" style="font-size:13px">🏠 ホーム</a>
</header>
<div class="wrap">
 <nav id="side"></nav>
 <main id="main"></main>
</div>
<footer>FELLOWS貸切 / フェローズ学園 資料Wiki — Obsidian金庫から自動生成。項目は相互リンクしています。</footer>
<script>
const DB = __PAYLOAD__;
const P = DB.pages, IDX = DB.index, ICON = DB.icons;
const side = document.getElementById('side'), main = document.getElementById('main'), q = document.getElementById('q');

function buildSide(filter){
 filter = (filter||'').trim().toLowerCase();
 let h = '';
 for(const c of DB.order){
  const groups = IDX[c]||[];
  let inner = '', total = 0;
  for(const [label, items] of groups){
   const its = filter ? items.filter(t => t.toLowerCase().includes(filter)) : items;
   if(!its.length) continue;
   total += its.length;
   const links = its.map(t => `<a href="#${encodeURIComponent(t)}" data-t="${encodeURIComponent(t)}">${t}</a>`).join('');
   if(label){
    const open = !!filter;  // 検索中は該当行を開く。通常は折りたたみ
    inner += `<div class="grp${open?' open':''}"><span class="tw">${open?'▾':'▸'}</span>${label}<span class="gn">${its.length}</span></div>`
           + `<div class="grpwrap"${open?'':' style="display:none"'}>${links}</div>`;
   } else {
    inner += links; // フラット（グループなし）
   }
  }
  if(!total) continue;
  h += `<h4>${ICON[c]||''} ${c}（${total}）</h4>` + inner;
 }
 side.innerHTML = h || '<p style="color:var(--muted);padding:8px">該当なし</p>';
 markActive();
}
function markActive(){
 const cur = decodeURIComponent(location.hash.slice(1));
 side.querySelectorAll('a').forEach(a=>a.classList.toggle('on', decodeURIComponent(a.dataset.t||'')===cur));
 const on = side.querySelector('a.on');
 if(on){
  const w = on.closest('.grpwrap');
  if(w && w.style.display==='none'){
   w.style.display=''; const g=w.previousElementSibling;
   if(g && g.classList.contains('grp')){ g.classList.add('open'); const tw=g.querySelector('.tw'); if(tw) tw.textContent='▾'; }
  }
 }
}
function chip(list){
 return '<div class="chips">'+list.map(t=>P[t]?`<a href="#${encodeURIComponent(t)}">${t}</a>`:'').join('')+'</div>';
}
function render(){
 let t = decodeURIComponent(location.hash.slice(1)) || '00_HOME';
 const pg = P[t];
 if(!pg){ main.innerHTML = '<h1 class="pt">見つかりません</h1><p>この項目はありません。左の一覧か検索から選んでください。</p>'; return; }
 let info = '';
 if(pg.info && pg.info.length && t!=='00_HOME'){
  info = '<div class="infobox"><table>'+pg.info.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`).join('')+'</table></div>';
 }
 let rel = '';
 if(t!=='00_HOME'){
  if(pg.links && pg.links.length) rel += `<div class="rel"><h3>🔗 関連項目</h3>${chip(pg.links)}</div>`;
  if(pg.back && pg.back.length) rel += `<div class="rel"><h3>↩ ここにリンクしている項目（${pg.back.length}）</h3>${chip(pg.back)}</div>`;
 }
 main.innerHTML = `<div class="crumb">${ICON[pg.cat]||''} ${pg.cat}</div>`+
  `<h1 class="pt">${t}<span class="badge">${pg.type||pg.cat}</span></h1>`+
  info + `<div class="art">${pg.html}</div>` + rel;
 window.scrollTo(0,0); markActive();
}
q.addEventListener('input', ()=>buildSide(q.value));
q.addEventListener('keydown', e=>{ if(e.key==='Enter'){ const a=side.querySelector('a'); if(a) location.hash=a.getAttribute('href'); }});
window.addEventListener('hashchange', render);
// ---- 目次: 五十音の行見出しを押すと開閉（アコーディオン） ----
side.addEventListener('click', e=>{
 const g = e.target.closest('.grp');
 if(!g) return;
 const w = g.nextElementSibling;
 if(!w || !w.classList.contains('grpwrap')) return;
 const show = w.style.display === 'none';
 w.style.display = show ? '' : 'none';
 g.classList.toggle('open', show);
 const tw = g.querySelector('.tw'); if(tw) tw.textContent = show ? '▾' : '▸';
});
// ---- モバイル：目次ドロワーの開閉 ----
const menu=document.getElementById('menu');
const isMobile=()=>matchMedia('(max-width:820px)').matches;
menu.addEventListener('click', ()=>document.body.classList.toggle('nav-open'));
side.addEventListener('click', e=>{ if(e.target.closest('a')) document.body.classList.remove('nav-open'); });
q.addEventListener('input', ()=>{ if(isMobile() && q.value.trim()) document.body.classList.add('nav-open'); });
window.addEventListener('hashchange', ()=>document.body.classList.remove('nav-open'));
buildSide(''); render();
</script>
</body></html>"""

open(OUT, "w", encoding="utf-8").write(HTML.replace("__PAYLOAD__", payload))
print("WROTE", OUT, "| pages:", len(data))
for c in CAT_ORDER: print(" ", c, len(index.get(c,[])))
