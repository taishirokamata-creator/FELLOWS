# -*- coding: utf-8 -*-
"""fellows_db.json -> Obsidian vault (markdown + [[wikilinks]])"""
import json, os, re, shutil

# パス可搬化：このスクリプトは <FELLOWS>/年表/build/ に置く前提。
# BASE = FELLOWS フォルダ（= build の2つ上）。PC・ユーザー名・ドライブが変わっても自動追従。
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))
VAULT = os.path.join(BASE, "FELLOWS_Vault")
shutil.rmtree(VAULT, ignore_errors=True)  # 全自動生成（手編集前提なし）

# 人物ノートと同名衝突を避けるための設定ノート表示名の上書き
WORLD_DISPLAY = {"ギャラガー": "ギャラガー計画（AI）"}
def wdisp(k): return WORLD_DISPLAY.get(k, k)
db = json.load(open(os.path.join(BASE, "年表", "data", "fellows_db.json"), encoding="utf-8"))

def sanitize(name):
    return re.sub(r'[\\/:*?"<>|\n]+', "・", name).strip()

def w(folder, fname, text):
    d = os.path.join(VAULT, folder)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, sanitize(fname) + ".md"), "w", encoding="utf-8") as f:
        f.write(text)

# ---------- 公演: 短縮タイトル & 接続マップ ----------
SHORT = {
 "story-sep":"ストーリー人狼9月編","story-oct":"ハロウィン人狼（10月編）","shino":"シノの魂",
 "meison":"メイソン編","xmas":"サンタ人狼（クリスマス編）","special":"FELLOWSスペシャル人狼",
 "openeyes":"オープン・ザ・アイズ","lastxmas":"ラストクリスマスの逆襲","lastxmas-remake":"ラストクリスマスの逆襲 リメイク",
 "space":"FELLOWS、宇宙へ","naoki":"NAOKI EMPIRE INVASION","moon":"フェロウズ、月へ",
 "future":"フェロウズ、未来へ","never":"NEVER！NEVER！NEVER！","thishistory":"This is history, this is history, right here, right now, this is history","keyagu":"ケヤグセカイ",
 # ---- 今回追加の公演 ----
 "nakama":"ナカマセカイ","nameku":"FELLOWS、ナメック星へ","getback":"Get Back",
 "ginga-red":"銀河鉄道の夜 赤","ginga-blue":"銀河鉄道の夜 青","fourth":"なぞの四人目の男",
 "tenka":"天下一武狼会シリーズ","naoki-close":"NAOKI CLOSE","valentine":"バレンタイン告白大作戦人狼",
 "gakuenz":"FELLOWS学園Z","kaiju":"怪獣",
 "tenka4":"失われた天下一武狼会 第4回の記憶","tenka-gendai":"現代版天下一武狼会",
}
CONNECT = {
 "story-sep":["keyagu"], "story-oct":["story-sep"], "shino":["future","space","naoki"],
 "meison":["xmas"], "xmas":["meison","lastxmas"], "special":["openeyes"], "openeyes":["special"],
 "lastxmas":["xmas","lastxmas-remake","space"], "lastxmas-remake":["lastxmas"],
 "space":["shino","naoki","future"], "naoki":["shino","space","moon"], "moon":["space","naoki","future"],
 "future":["space","moon","naoki","shino"], "never":["future"], "thishistory":["keyagu","shino"],
 "keyagu":["thishistory","story-sep"],
 "nakama":["keyagu","thishistory"], "nameku":["future","getback","tenka4"], "naoki-close":["naoki"],
 "ginga-red":["ginga-blue"], "ginga-blue":["ginga-red"],
 "tenka":["tenka4","tenka-gendai"], "tenka4":["tenka","future","nameku","tenka-gendai"], "tenka-gendai":["tenka","tenka4"],
}
# 作中年表/HOMEで公演を並べる順（新規は末尾に）
STORY_ORDER = ["story-sep","story-oct","nakama","shino","meison","xmas","special","openeyes",
 "lastxmas","lastxmas-remake","never","space","naoki","naoki-close","moon","future","nameku",
 "getback","fourth","ginga-red","ginga-blue","tenka-gendai","tenka","tenka4","valentine","gakuenz","kaiju","thishistory","keyagu"]
ev_by_id = {e["id"]: e for e in db["events"]}

# ---------- 人物: 正規名 & エイリアス（イベント配役の突合用） ----------
# canonical filename : {"gen","desc","aliases":[...],"kin":[related canonical names]}
CHARS = {
 "しのぴ":{"gen":"創始者／GM","aliases":["しの","しのぴ","学園長","AIしのぴ","ぴろうず","りょー"],
   "kin":["にゃんぽ子","ギャラガー"],
   "desc":"FELLOWS貸切主催・GM。青森出身。人間しのぴは2033年に病死し、以後 AIしのぴ→（超未来では）ぴろうず として物語全体を貫く“世界そのもの”。"},
 "阿部洸希":{"gen":"現実世代（親）","aliases":["阿部洸希","阿部洸季","阿部"],"kin":["ア・バイバイ","ガッツ石松"],
   "desc":"人狼ルームGM／終身名誉GM。レジェンド。孫世代が安倍（ア・バイバイ）。"},
 "メイソン":{"gen":"現実世代（親）","aliases":["メイソン"],"kin":[],
   "desc":"人狼ルーム専属プレイヤーの自由人レジェンド。カミングアウター村の考案者。"},
 "人狼ルームGM・レジェンド勢":{"gen":"現実世代（親）","aliases":["柏村","浦","仲田","富山","とみー","石丸","児玉"],"kin":["なおき"],
   "desc":"柏村・浦・仲田・富山(とみー)・石丸・児玉ら、人狼ルームのGM／レジェンド勢。子世代の親・祖父にあたる。"},
 "なおき":{"gen":"現実世代（親）→AI","aliases":["なおき","NAOKI"],"kin":["人狼ルームGM・レジェンド勢"],
   "desc":"スイーツ人狼ルームGM。2025年に人狼ルームへ移籍→反発層が『スイーツ派』を結成。子孫がAI『NAOKI』を作り、なおき帝国の王となる。"},
 "にゃんぽ子":{"gen":"親→子","aliases":["にゃんぽこ","にゃんぽ子"],"kin":["しのぴ"],
   "desc":"親＝にゃんぽこ、子＝にゃんぽ子。『フェロウズ、未来へ』でしのぴから学園長を引き継ぐ。"},
 "イム・スヒョン":{"gen":"親→子","aliases":["イムラ","イム・スヒョン","イムスヒョン"],"kin":[],
   "desc":"親＝イムラ（アルティメット人狼出演）。子＝イム・スヒョンは宇宙船の操縦を任される中心格。"},
 "脇脇脇男":{"gen":"親→子","aliases":["脇脇脇男","わっき","ワキヤス"],"kin":[],
   "desc":"親＝わっき〜。子＝脇脇脇男（勘が鋭い）。改名メタでは“ワキヤスメ・アツコ”とも。"},
 "みの":{"gen":"親→子","aliases":["みの","マノ"],"kin":[],
   "desc":"親＝マノ。子＝みの（みのミュージック）。音楽・ビートルズ好きで、サンタどっきりの発案者。"},
 "アウトオブウメコ":{"gen":"親→子／改名","aliases":["アウトオブウメコ","ウメコ","梅田","小梅"],"kin":[],
   "desc":"スイーツ人狼ルーム店長の子＝梅田。改名メタでアウトオブウメコに。"},
 "クニタケチユキ":{"gen":"親→子","aliases":["クニタケ","ちゆっき"],"kin":[],
   "desc":"親＝ちゆっきー。子＝バンド THE FOREVER YOUNG（エバヤン）のボーカル。『FELLOWS』の名の由来に関わる。"},
 "J／F":{"gen":"親→子","aliases":["J","F"],"kin":[],
   "desc":"親＝J（唯一無二のエンターテイナー）。子＝F。"},
 "にまる":{"gen":"親→子","aliases":["にまる","ななまる"],"kin":[],
   "desc":"母＝ななまる。子＝にまる（“母より5足りない”）。"},
 "ひ子":{"gen":"親→子","aliases":["ひこにゃん","ひ子","ひこにゃ"],"kin":[],
   "desc":"滋賀のゆるキャラの系譜。子＝ひ子（すー夫の妻）。"},
 "三田村（ミコ）":{"gen":"新入生","aliases":["三田村","ミコ"],"kin":[],
   "desc":"元ラストクリスマスのスパイ→和解して入学。以後の惑星編にレギュラー出演。"},
 "タグチ姉弟":{"gen":"惑星の子孫","aliases":["チョモ","ワ・タック","たぐっちょ","わたく"],"kin":["ギャラガー"],
   "desc":"アトラス星の姉弟チョモ＆ワ。祖父母たぐっちょ・わたくは2043年に地球を去ったFELLOWS。『宇宙へ』で入学。"},
 "NAOKI":{"gen":"惑星／AI","aliases":["NAOKI"],"kin":["なおき","ギャラガー"],
   "desc":"なおきの分身AI。スイーツ派が2043年の移住先で作成。帝国ごと学園と合併する。"},
 "月の狼男（ストレンジディックス）":{"gen":"惑星の子孫","aliases":["フレディ","ペレッペ","Y-指定"],"kin":[],
   "desc":"月に住むヒップホップ狼男の一家（フレディ／DJペレッペ／Y-指定）。"},
 "ギャラガー":{"gen":"AI","aliases":["ギャラガー"],"kin":["しのぴ"],
   "desc":"AIしのぴが各惑星のFELLOWSの子孫を集めるために作り続けたAI群。正体は『フェロウズ、未来へ』で判明。"},
 "ア・バイバイ":{"gen":"子／改名","aliases":["ア・バイバイ","安倍"],"kin":["阿部洸希"],
   "desc":"祖父＝阿部洸希、父＝某首相。ビートルズ好き。改名メタでア・バイバイに。"},
 "ハマ・ヤンクミ":{"gen":"子世代","aliases":["ハマ・ヤンクミ","ハマヤン"],"kin":[],
   "desc":"某熱血教師の子孫。なぜか関西弁。学級委員長格。"},
 "ヘンリー王子":{"gen":"子世代","aliases":["ヘンリー"],"kin":[],
   "desc":"かの有名なヘンリー王子の子孫。でも父は新潟産まれ。"},
 "L":{"gen":"子世代","aliases":["L"],"kin":[],
   "desc":"惑星編で活躍する冷静な推理役。NAOKI帝国編・月編に登場。"},
 "三田村以外の新入生ほか":{"gen":"子世代・新入生","aliases":["ストーブ","たくや","きゅうまる","まぐろ","ルイ","幸子","いと","夏子","すー夫","グッチ","ガッツ石松","はちお","はちまる"],"kin":[],
   "desc":"ヘンリー王子・ストーブ・たくや・まぐろ・％・G・ルイ1444世・幸子・いと・夏子・すー夫・グッチ裕三・ガッツ石松・はちお 等、個性豊かなFELLOWS学園の生徒たち。"},
 "カコ（かちょぱ）":{"gen":"敵→仲間","aliases":["カコ","かちょぱ"],"kin":[],
   "desc":"『ラストクリスマスの逆襲 リメイク』の潜入スパイ（演：かっくん）。組織ラストクリスマスの側近だが、学園の子供達に触れて心が変わっていく。"},
 "やま爺":{"gen":"NPC","aliases":["やま爺"],"kin":[],
   "desc":"『フェロウズ、月へ』の結末で、崩壊する月から逃れた月の民（狼男）を地球で受け入れるNPC。ラップを刻む。"},
 "びじょん":{"gen":"被害者／＝ぴろうず","aliases":["びじょん"],"kin":["しのぴ"],
   "desc":"『ナカマセカイ』の被害者。その正体はぴろうず＝しのぴ。“ナカマセカイ事変”で死亡したとされる存在。"},
 "ドクターペロ":{"gen":"敵／人造人間","aliases":["ドクターペロ","ペロ"],"kin":["にゃんぽ子"],
   "desc":"『失われた天下一武狼会 第4回の記憶』の襲来者。最強の人狼を求め自らを改造した異形の人造人間。同じ人造の存在にゃんぽ子を取り込み完全体化し、奪還を賭けた“ペロゲーム”を仕掛ける。滅ぼすのではなく“最高の人狼ゲームで楽しむ”のが目的。"},
 "こまるぞぅ":{"gen":"子世代（新入生）","aliases":["こまるぞぅ"],"kin":[],
   "desc":"「困るぞぅ」が口癖の生徒。第4回天下一武狼会では“まだ入学していないのに呼ばれて困る”と言いつつ奮闘。"},
 "音楽と政治、両方尊重♥":{"gen":"子世代","aliases":["音楽と政治"],"kin":[],
   "desc":"「人狼にもいろんな在り方がある」と多様な考え方を尊重する生徒。人間改造の話には強く反応する。"},
 "なっち（ねえ笑って？）":{"gen":"子世代","aliases":["なっち"],"kin":[],
   "desc":"「最後はみんな笑って終われるといいよね」が信条の生徒。天下一武狼会でも“ちゃんと笑える日”を願う。"},
 "ひらり":{"gen":"子世代","aliases":["ひらり"],"kin":[],
   "desc":"祖父も優勝経験があるという生徒。第4回大会では“空から嫌な音”＝ドクターペロの襲来をいち早く察知する。"},
}

def cast_clean(s):
    s = s.strip()
    s = re.sub(r'（PL[^）]*）|（演じる[^）]*）', '', s)
    s = re.sub(r'\((?:GM|NPC|電話|サンタ|開眼野郎|新学園長|最高顧問として残る結末も|2016|1978|GM/3人目|GM・3人目)\)', '', s)
    s = re.sub(r'（(?:GM|NPC|新学園長|サンタ)）', '', s)
    return s.strip()

def canon_for(raw):
    """イベント配役 raw -> 正規人物名 or None"""
    c = cast_clean(raw)
    for name, meta in CHARS.items():
        for a in meta["aliases"]:
            if len(a) <= 1:
                if c == a or c.split("／")[0] == a or c.split("/")[0] == a:
                    return name
            elif a in c:
                return name
    return None

def link_name(raw):
    """正規化できない配役の“主表記”をノート名に（／・( の前を採る）"""
    c = re.split(r'[／/（(]', cast_clean(raw))[0].strip()
    return c or cast_clean(raw)

node_appears = {}  # ノート名(正規 or 端役) -> 出演公演idリスト

# 各人物の出演公演を自動集計
appears = {name: [] for name in CHARS}
for e in db["events"]:
    seen = set()
    for raw in e.get("chars", []):
        cn = canon_for(raw)
        if cn and e["id"] not in seen and cn not in [x for x in appears if e["id"] in appears[x]]:
            appears.setdefault(cn, [])
            if e["id"] not in appears[cn]:
                appears[cn].append(e["id"])
            seen.add(cn)

# ---------- 設定（世界観）: マッチトークン ----------
WORLD_MATCH = {
 "人狼ルーム":["人狼ルーム"], "FELLOWS貸切":["FELLOWS貸切","貸切"], "FELLOWS学園":["FELLOWS学園","学園"],
 "AIしのぴ":["AIしのぴ","しのぴAI","AIしの"], "悪いAI地球襲来事変（2043年）":["2043","悪いAI","AI戦争","宇宙外生命体"],
 "ギャラガー":["ギャラガー"], "NAOKI GAME / なおき帝国":["NAOKI","なおき帝国","スイーツ派"],
 "アトラス星 / 月 / なおき帝国":["アトラス","月","帝国","惑星"], "ブレイン（脳）":["ブレイン","5524"],
 "青森 / ハピゲ":["青森","ハピゲ","緑林"], "改名メタ（2024年3月〜）":["改名","バグ"],
 "合言葉「We are FELLOWS!!」":["We are","FELLOOO"],
}
def worlds_for_event(e):
    hay = e.get("synopsis","") + e.get("logline","") + " ".join(e.get("world",[]))
    out = []
    for wk, toks in WORLD_MATCH.items():
        if any(t in hay for t in toks):
            out.append(wk)
    return out

# ---------- 生成: 公演ノート ----------
for e in db["events"]:
    st = SHORT.get(e["id"], e["title"])
    cast_nodes = []
    for raw in e.get("chars", []):
        cn = canon_for(raw)
        node = cn if cn else link_name(raw)
        if node and node not in cast_nodes:
            cast_nodes.append(node)
    for node in cast_nodes:
        node_appears.setdefault(node, [])
        if e["id"] not in node_appears[node]:
            node_appears[node].append(e["id"])
    cast_links = [f"[[{sanitize(n)}]]" for n in cast_nodes]
    conn = " / ".join(f"[[{sanitize(SHORT.get(i, ev_by_id[i]['title']))}]]" for i in CONNECT.get(e["id"], []))
    wl = " / ".join(f"[[{sanitize(wdisp(wk))}]]" for wk in worlds_for_event(e))
    body = f"""---
type: 公演
aliases: ["{e['title']}"]
シリーズ: {e['series']}
現実開催日: {e['real_date']}
作中年代: {e['iu_date']}
tags: [公演, FELLOWS]
---
> [!quote] {e['logline']}

**シリーズ**：{e['series']}
**現実の開催日**：{e['real_date']}　｜　**作中年代**：{e['iu_date']}

## あらすじ
{e['synopsis']}

## 登場人物
{"　".join(cast_links) if cast_links else "—"}

## 世界観・キーワード
{wl if wl else "—"}
{chr(10).join("- " + x for x in e.get("world", []))}

## つながり（前後の公演）
{conn if conn else "—"}

---
🏠 [[00_HOME]]　｜　🌏 [[作中年表]]　｜　🗓 [[現実の開催史]]
"""
    w("公演", st, body)

# ---------- 生成: 人物ノート（主要＝リッチ） ----------
for name, meta in CHARS.items():
    apps = " / ".join(f"[[{sanitize(SHORT.get(i, ev_by_id[i]['title']))}]]" for i in node_appears.get(name, appears.get(name, [])))
    kin = " / ".join(f"[[{sanitize(k)}]]" for k in meta["kin"]) if meta["kin"] else "—"
    body = f"""---
type: 人物
世代: {meta['gen']}
aliases: {json.dumps(meta['aliases'], ensure_ascii=False)}
tags: [人物, FELLOWS]
---
# {name}
**世代**：{meta['gen']}

{meta['desc']}

## 血縁・関連人物
{kin}

## 出演公演
{apps if apps else "—"}

---
🏠 [[00_HOME]]
"""
    w("人物", name, body)

# ---------- 生成: 端役ノート（1回でも出たキャラを自動ノート化） ----------
authored = set(CHARS.keys())
minor_count = 0
for node, evids in sorted(node_appears.items()):
    if node in authored or not node:
        continue
    apps = " / ".join(f"[[{sanitize(SHORT.get(i, ev_by_id[i]['title']))}]]" for i in evids)
    tag = "端役" if len(evids) == 1 else "脇役"
    body = f"""---
type: 人物
世代: {tag}
tags: [人物, FELLOWS, {tag}]
---
# {node}
（配役から自動生成：{tag}）

## 出演公演
{apps}

---
🏠 [[00_HOME]]
"""
    w("人物", node, body)
    minor_count += 1

# ---------- 生成: キーワード（特殊用語）ノート ----------
reserved = {sanitize(SHORT.get(e["id"], e["title"])) for e in db["events"]}
reserved |= {sanitize(n) for n in CHARS.keys()} | {sanitize(n) for n in node_appears.keys()}
reserved |= {sanitize(wdisp(wd["k"])) for wd in db["world"]}
kw_count = 0; kw_names = []
for kw in db.get("keywords", []):
    fname = kw["k"] + "（用語）" if sanitize(kw["k"]) in reserved else kw["k"]
    kw_names.append(fname)
    see = " / ".join(f"[[{sanitize(s)}]]" for s in kw.get("see", [])) or "—"
    used = []
    for e in db["events"]:
        hay = e.get("synopsis","") + " " + " ".join(e.get("world",[])) + " " + " ".join(e.get("chars",[]))
        if kw["k"] in hay or any(t in hay for t in kw["k"].replace("／","/").split("/") if len(t) >= 2):
            used.append(SHORT.get(e["id"], e["title"]))
    ul = " / ".join(f"[[{sanitize(u)}]]" for u in dict.fromkeys(used)) or "—"
    body = f"""---
type: キーワード
aliases: ["{kw['k']}"]
tags: [キーワード, 用語, FELLOWS]
---
# {kw['k']}

{kw['v']}

## 関連
{see}

## 登場する公演
{ul}

---
🏠 [[00_HOME]]
"""
    w("キーワード", fname, body)
    kw_count += 1

# ---------- 生成: 設定ノート ----------
for wd in db["world"]:
    used = [SHORT[e["id"]] for e in db["events"] if wd["k"] in worlds_for_event(e)]
    ul = " / ".join(f"[[{sanitize(s)}]]" for s in used)
    body = f"""---
type: 設定
aliases: ["{wd['k']}"]
tags: [設定, 世界観, FELLOWS]
---
# {wdisp(wd['k'])}

{wd['v']}

## 登場する公演
{ul if ul else "—"}

---
🏠 [[00_HOME]]
"""
    w("設定", wdisp(wd["k"]), body)

# ---------- 生成: 作中年表（FELLOWS世界の人狼・作中年代の線表） ----------
def _first_year(s):
    if "5524" in s: return 5524
    m = re.search(r"(\d{4})", s)
    return int(m.group(1)) if m else None
EV_IU_NUM = {  # iu_dateが非数値/枠組み表記の公演の作中年を補正
 "story-sep":2023, "story-oct":1978, "getback":2024, "nakama":2024,
 "fourth":2026, "ginga-red":2026, "ginga-blue":2026, "keyagu":5524,
 "kaiju":2200, "naoki-close":2075, "tenka-gendai":2025, "nameku":2076,
}
EV_SKIP = {"tenka"}  # 総称シリーズは線表から除外
def _ev_num(e):
    if e["id"] in EV_IU_NUM: return EV_IU_NUM[e["id"]]
    return _first_year(e["iu_date"]) or 9999
def _year_header(num):
    sp = {1978:"1978年（ハロウィン・劇中設定）", 2200:"2XXX年（学園史よりはるか未来）",
          5524:"西暦5524年（超未来）", 9999:"作中年代 未確定"}
    return sp.get(num, f"{num}年")

_tl = {}
for c in db["canon"]:
    n = _first_year(c["year"]) or 9999
    _tl.setdefault(n, []).append(("📌", None, c["title"], c["detail"], c.get("warn")))
for e in db["events"]:
    if e["id"] in EV_SKIP: continue
    n = _ev_num(e)
    _tl.setdefault(n, []).append(("🎭", SHORT.get(e["id"], e["title"]), e["title"], e["logline"], False))

tl_lines = []
for n in sorted(_tl):
    tl_lines.append(f"### {_year_header(n)}")
    for icon, link, title, blurb, warn in sorted(_tl[n], key=lambda x: (x[0] != "📌",)):
        head = f"[[{sanitize(link)}]]" if link else f"**{title}**"
        w_ = "　⚠️年に揺れあり" if warn else ""
        tl_lines.append(f"- {icon} {head}{w_} — {blurb}")
    tl_lines.append("")
canon_body = f"""---
type: 年表
tags: [年表, 作中, FELLOWS]
---
# 🌏 作中年表 ― FELLOWS世界の人狼

人狼ルーム発『FELLOWS世界の人狼』の作中年代の年表。原点の人狼ルームから超未来まで、各ストーリー（**FELLOWS学園もそのひとつ**）を作中の時系列で並べています。📌＝世界の出来事／🎭＝各公演（クリックでページへ）。

{chr(10).join(tl_lines)}
---
🏠 [[00_HOME]]　｜　🗓 [[現実の開催史]]
"""
w("年表", "作中年表", canon_body)

# ---------- 生成: 現実の開催史（開催日 / 公演 / 内容） ----------
def realkey(e):
    m = re.search(r'(\d{4})年(\d{1,2})?月?(\d{1,2})?', e["real_date"])
    if not m: return (9999, 99, 99)
    return (int(m.group(1)), int(m.group(2)) if m.group(2) else 99,
            int(m.group(3)) if m.group(3) else 99)
rows = sorted(db["events"], key=realkey)
real_body = """---
type: 年表
tags: [年表, 開催史, FELLOWS]
---
# 🗓 現実の開催史（いつ何を上演したか）

『FELLOWS世界の人狼』を実際に上演した日付順。公演名からページへ飛べます。

| 現実の開催日 | 公演 | 内容 |
|---|---|---|
""" + "\n".join(
 f"| {e['real_date']} | [[{sanitize(SHORT[e['id']])}]] | {e['logline'].replace('|','／')} |" for e in rows
) + """

🏠 [[00_HOME]]　｜　🌏 [[作中年表]]
"""
w("年表", "現実の開催史", real_body)

# ---------- 生成: HOME (MOC) ----------
home = f"""---
type: MOC
tags: [HOME, FELLOWS]
---
# 🐺 FELLOWS貸切 / FELLOWS学園 — 資料金庫

人狼ルーム『FELLOWS貸切』のストーリー人狼と、近未来SF『FELLOWS学園』の設定データベース。
このノートを起点に、公演・人物・世界観・年表が `[[リンク]]` で繋がっています（左のグラフビューで全体像が見えます）。

## 🗺 まず見る
- [[作中年表]] — FELLOWS世界の人狼の作中年代（人狼ルーム→超未来）
- [[現実の開催史]] — いつ何を上演したか

## 📖 公演（作中年代順）
""" + "\n".join(
 f"- [[{sanitize(SHORT[i])}]]" for i in STORY_ORDER if i in ev_by_id
) + "\n\n## 👥 人物（主要）\n" + "　".join(f"[[{sanitize(n)}]]" for n in CHARS) + \
   f"\n\n> ほか、単発・脇役キャラも各公演から自動でノート化されています（`tags:端役/脇役`）。人物ノート総数 {len(CHARS)+minor_count}。" + \
   "\n\n## 🔑 世界観設定\n" + "　".join(f"[[{sanitize(wdisp(wd['k']))}]]" for wd in db["world"]) + \
   "\n\n## 🧩 特殊キーワード（用語集）\n" + "　".join(f"[[{sanitize(n)}]]" for n in kw_names) + \
   "\n\n---\n*生成元：`年表/data/fellows_db.json`。追記はJSON→再生成、またはノートを直接編集。*\n"
with open(os.path.join(VAULT, "00_HOME.md"), "w", encoding="utf-8") as f:
    f.write(home)

# ---------- 個別人物インデックス（index.html の人物名鑑用：1人=1エントリ） ----------
people_out = []
for node, evids in sorted(node_appears.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    if not node:
        continue
    meta = CHARS.get(node)
    gen = meta["gen"] if meta else ("端役" if len(evids) == 1 else "脇役")
    desc = meta["desc"] if meta else ""
    kin = meta["kin"] if meta else []
    people_out.append({
        "name": node,
        "gen": gen,
        "desc": desc,
        "events": [SHORT.get(i, ev_by_id[i]["title"]) for i in evids],
        "n": len(evids),
        "kin": kin,
        "authored": bool(meta),
    })
with open(os.path.join(BASE, "年表", "data", "people_index.json"), "w", encoding="utf-8") as f:
    json.dump(people_out, f, ensure_ascii=False, indent=1)

# 集計
counts = {d: len([x for x in os.listdir(os.path.join(VAULT, d)) if x.endswith(".md")])
          for d in ["公演","人物","設定","年表"]}
print("VAULT:", VAULT)
print("notes:", counts, "+ 00_HOME.md")
print("people_index.json:", len(people_out), "人")
