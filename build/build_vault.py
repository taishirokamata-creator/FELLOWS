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
 "story-sep":"FELLOWS貸切誕生！","story-oct":"ハロウィン人狼（10月編）","shino":"シノの魂",
 "meison":"FELLOWS学園の人狼（阿部おじ＆メイソンおじ襲来）","xmas":"FELLOWS学園の人狼（クリスマス編）","special":"FELLOWS学園新年会",
 "openeyes":"オープン・ザ・アイズ","lastxmas":"ラストクリスマスの逆襲","lastxmas-remake":"ラストクリスマスの逆襲 リメイク",
 "space":"フェロウズ、宇宙へ","naoki":"NAOKI EMPIRE INVASION","moon":"フェロウズ、月へ",
 "future":"フェロウズ、未来へ","never":"NEVER！NEVER！NEVER！","thishistory":"This is history, this is history, right here, right now, this is history","keyagu":"ケヤグセカイ",
 # ---- 今回追加の公演 ----
 "nakama":"ナカマセカイ","nameku":"FELLOWS、ナメック星へ","getback":"replica／get back",
 "ginga-red":"銀河鉄道の夜 赤","ginga-blue":"銀河鉄道の夜 青","fourth":"なぞの四人目の男",
 "valentine":"バレンタイン告白大作戦",
 "gakuenz":"FELLOWS学園Z","kaiju":"怪獣",
 "tenka4":"失われた天下一武狼会 第四回の記憶",
 "sim100":"Simulation #100","kronos":"クロノス・プロトコル","believe":"FELLOWS外伝 ―Believe―",
}
CONNECT = {
 "story-sep":["keyagu"], "story-oct":["story-sep"], "shino":["future","space","naoki"],
 "meison":["xmas"], "xmas":["meison","lastxmas"], "special":["openeyes"], "openeyes":["special"],
 "lastxmas":["xmas","lastxmas-remake","space"], "lastxmas-remake":["lastxmas"],
 "space":["shino","naoki","future"], "naoki":["shino","space","moon"], "moon":["space","naoki","future"],
 "future":["space","moon","naoki","shino"], "never":["future"], "thishistory":["keyagu","shino"],
 "keyagu":["thishistory","story-sep"],
 "nakama":["keyagu","thishistory"], "nameku":["future","getback","tenka4"],
 "ginga-red":["ginga-blue"], "ginga-blue":["ginga-red"],
 "tenka4":["future","nameku"],
 "sim100":["shino"], "kronos":["nameku","future"], "believe":["story-sep"],
}
# 作中年表/HOMEで公演を並べる順（新規は末尾に）
STORY_ORDER = ["story-sep","story-oct","nakama","sim100","shino","meison","xmas","special","openeyes",
 "lastxmas","lastxmas-remake","never","space","naoki","moon","future","nameku","kronos",
 "getback","fourth","ginga-red","ginga-blue","tenka4","valentine","gakuenz","kaiju","thishistory","keyagu","believe"]
ev_by_id = {e["id"]: e for e in db["events"]}

# ---------- 本人ロスター（参加者ランキングPDF＝実在プレイヤー／GM） ----------
# ここに載る名前は「本人」。載っていない配役は既定で「作中キャラ」。
PERSON_ROSTER = set("""
ちゆっきー にゃんぽこ わっき〜 イムラ 小梅 マノ J うに きむら ハマヤン ひこにゃん へんりー
さっちん こたつ ななまる グッチー るい イトウ みた のりちゃん まりちゃん やまぴー たぐっちょ わたく
もんた ゆっくん いちえ くおん ぺぺぺのぺ Azma もなみん カリアゲ おおちゃん ひらりー さく太 フルヤ
ゆみ えすえる らび ゆずこしょー 武流 むーちゃん ケルカー かっくん ぴほ さざえ いもすけ タケル すー
りんご ドラえもん かふゆ バンバン ネオ もっちー ちゃんほみ りんこ ほしゆめ ちょぴん ぱる げん
きゃのん ししょう さくら natsumi マナフィ ルーカス コロン だんちょー リキゾー しんた ミヤオ せいじ
ぐぐ ヨースケ はしもと ぶんすけ みっくす こんゆえ りっきー ぽろん れな みうたぴ じゅんぺー 新保 ゾノ
木下 うら みなちゃん saku かんちゃん たけい かろ のし なごちー サイケルダー るる けめこ HAL けーすけ
ほろ Natsuo ぴくせる のん せの John ちょうめい yukina さえき はるか しゅう サウザー
阿部 浦 仲田 富山 柏村 アリサ メイソン 石丸 なおき 児玉 とみー
""".split())

# ---------- 人物: 正規名 & エイリアス（イベント配役の突合用） ----------
# canonical filename : {"kind":"本人"/"キャラ","gen","desc","aliases":[...],"kin":[...]}
# 本人（親）と作中キャラ（子）は別エントリ。配役トークンで自動的に振り分ける。
CHARS = {
 # ===== 本人（実在プレイヤー／GM。※ロスターの他プレイヤーは配役から自動生成） =====
 "しの":{"kind":"本人","gen":"創始者／GM","aliases":["しの"],"kin":["学園長しのぴ","にゃんぽこ"],
   "desc":"FELLOWS貸切の主催・GM。青森出身。作中では自身のAI（学園長しのぴ／AIしのぴ）や、超未来のぴろうずとして描かれる。"},
 "阿部洸希":{"kind":"本人","gen":"人狼ルームGM（レジェンド）","aliases":["阿部洸希","阿部洸季","阿部"],"kin":["ア・バイバイ"],
   "desc":"人狼ルームGM／終身名誉GM。学園のア・バイバイの祖父にあたる。"},
 "メイソン":{"kind":"本人","gen":"人狼ルーム専属プレイヤー","aliases":["メイソン"],"kin":[],
   "desc":"人狼ルームの専属ゲームプレイヤー。カミングアウター村の考案者。"},
 "柏村":{"kind":"本人","gen":"人狼ルームGM","aliases":["柏村"],"kin":[],
   "desc":"人狼ルームのGM。『なぞの四人目の男』の占いジジ役、銀河鉄道の案内人など進行役でよく登場。"},
 "富山貴記":{"kind":"本人","gen":"人狼ルームGM","aliases":["富山貴記","富山","とみー"],"kin":[],
   "desc":"人狼ルームのGM（とみー）。"},
 "浦":{"kind":"本人","gen":"人狼ルームGM","aliases":["浦"],"kin":[],
   "desc":"人狼ルームのGM。"},
 "仲田":{"kind":"本人","gen":"人狼ルームGM","aliases":["仲田"],"kin":[],
   "desc":"人狼ルームのGM。"},
 "児玉":{"kind":"本人","gen":"人狼ルームGM","aliases":["児玉"],"kin":[],
   "desc":"人狼ルームのGM。"},
 "アリサ":{"kind":"本人","gen":"人狼ルームGM","aliases":["アリサ"],"kin":["亜理紗は大変なものを盗んでいきました"],
   "desc":"人狼ルームのGM。作中キャラ『亜理紗は大変なものを盗んでいきました』を演じた本人。"},
 "なおき":{"kind":"本人","gen":"人狼ルームGM","aliases":["なおき"],"kin":["NAOKI"],
   "desc":"人狼ルームのGM（元はスイーツ人狼ルームGM）。2025年に人狼ルームへ移籍→反発層が『スイーツ派』を結成。子孫がAI『NAOKI』を作る。"},
 "石丸":{"kind":"本人","gen":"人狼ルームGM","aliases":["石丸"],"kin":["ガッツ石松"],
   "desc":"人狼ルームのGM。学園のガッツ石松の祖父（石丸将壮）にあたる。2025年3月で引退。"},
 # ===== 作中キャラ（学園の生徒・敵・AI 等） =====
 "学園長しのぴ":{"kind":"キャラ","gen":"AI（学園長）","aliases":["学園長しのぴ","学園長","AIしのぴ","しのぴAI","しのぴ","ぴろうず","りょー"],"kin":["しの","にゃんぽ子","ギャラガー"],
   "desc":"しのの意思を継ぐAI。学園長として学園を導く。超未来では『ぴろうず』として描かれる。"},
 "にゃんぽ子":{"kind":"キャラ","gen":"学園長（2代目）","aliases":["にゃんぽ子"],"kin":["にゃんぽこ","学園長しのぴ"],
   "desc":"にゃんぽこ（本人）の子にあたる学園キャラ。『フェロウズ、未来へ』でしのぴから学園長を引き継ぐ。"},
 "イム・スヒョン":{"kind":"キャラ","gen":"学園の生徒","aliases":["イム・スヒョン","イムスヒョン"],"kin":["イムラ"],
   "desc":"イムラ（本人）の子。宇宙船の操縦を任される中心格。"},
 "脇脇脇男":{"kind":"キャラ","gen":"学園の生徒","aliases":["脇脇脇男","ワキヤス"],"kin":["わっき〜"],
   "desc":"わっき〜（本人）の子。勘が鋭い。歴史改変（ゼンイセカイ）では“ワキヤスメ・アツコ”とも。"},
 "みの":{"kind":"キャラ","gen":"学園の生徒","aliases":["みの","みのミュージック"],"kin":["マノ"],
   "desc":"マノ（本人）の子。音楽・ビートルズ好き。サンタどっきりの発案者。"},
 "アウトオブウメコ":{"kind":"キャラ","gen":"学園の生徒","aliases":["アウトオブウメコ","ウメコ","梅田"],"kin":["小梅"],
   "desc":"小梅（本人）の子。歴史改変でアウトオブウメコに。"},
 "クニタケチユキ":{"kind":"キャラ","gen":"学園の生徒","aliases":["クニタケチユキ","クニタケ"],"kin":["ちゆっきー"],
   "desc":"ちゆっきー（本人）の子。バンド THE FOREVER YOUNG（エバヤン）のボーカルという設定。元ネタはエバヤンのクニタケヒロキ。"},
 "F":{"kind":"キャラ","gen":"学園の生徒","aliases":["F"],"kin":["J"],
   "desc":"J（本人）の子。"},
 "にまる":{"kind":"キャラ","gen":"学園の生徒","aliases":["にまる"],"kin":["ななまる"],
   "desc":"ななまる（本人）の子（“母より5足りない”）。"},
 "ひ子":{"kind":"キャラ","gen":"学園の生徒","aliases":["ひ子"],"kin":["ひこにゃん"],
   "desc":"ひこにゃん（本人）の系譜。すー夫の妻。"},
 "ハマ・ヤンクミ":{"kind":"キャラ","gen":"学園の生徒","aliases":["ハマ・ヤンクミ"],"kin":["ハマヤン"],
   "desc":"ハマヤン（本人）の子。学級委員長格。"},
 "ヘンリー王子":{"kind":"キャラ","gen":"学園の生徒","aliases":["ヘンリー王子","ヘンリー"],"kin":["へんりー"],
   "desc":"へんりー（本人）の系譜。"},
 "ア・バイバイ":{"kind":"キャラ","gen":"学園の生徒","aliases":["ア・バイバイ","安倍"],"kin":["阿部洸希"],
   "desc":"阿部洸希の孫。歴史改変で安倍→ア・バイバイに。"},
 "三田村ちゃん":{"kind":"キャラ","gen":"学園の生徒（新入生）","aliases":["三田村","ミコ"],"kin":[],
   "desc":"元ラストクリスマスのスパイ→和解して入学。惑星編にレギュラー出演。"},
 "NAOKI":{"kind":"キャラ","gen":"AI","aliases":["NAOKI"],"kin":["なおき","ギャラガー"],
   "desc":"なおきの分身AI。スイーツ派が2043年の移住先で作成。帝国ごと学園と合併する。"},
 "ギャラガー":{"kind":"キャラ","gen":"AI","aliases":["ギャラガー"],"kin":["学園長しのぴ"],
   "desc":"AIしのぴが各惑星のFELLOWSの子孫を集めるために作り続けたAI群。正体は『フェロウズ、未来へ』で判明。"},
 "L":{"kind":"キャラ","gen":"学園の生徒","aliases":["L"],"kin":[],
   "desc":"惑星編で活躍する推理役。NAOKI帝国編・月編に登場。"},
 "カコ（かちょぱ）":{"kind":"キャラ","gen":"敵→仲間","aliases":["カコ","かちょぱ"],"kin":[],
   "desc":"『ラストクリスマスの逆襲 リメイク』の潜入スパイ（演：かっくん）。組織ラストクリスマスの側近だが、学園の子供達に触れて心が変わる。"},
 "やま爺":{"kind":"キャラ","gen":"NPC","aliases":["やま爺"],"kin":[],
   "desc":"『フェロウズ、月へ』の結末で、崩壊する月から逃れた月の民（狼男）を地球で受け入れるNPC。"},
 "ぴじょん":{"kind":"キャラ","gen":"被害者","aliases":["ぴじょん"],"kin":["学園長しのぴ"],
   "desc":"『ナカマセカイ』の被害者。その正体はぴろうず＝しの。作中で殺され、死亡したとされる。"},
 "シャルル・モン・モンテスキュー":{"kind":"キャラ","gen":"天下一武狼会 第3回 MTF","aliases":["シャルル・モン・モンテスキュー","シャルル"],"kin":[],
   "desc":"天下一武狼会（学園版）第3回でMTFの称号を獲得したキャラクター。詳細はしのぴ確認事項。"},
 "ドクターペロ":{"kind":"キャラ","gen":"敵／人造人間","aliases":["ドクターペロ","ペロ"],"kin":["にゃんぽ子"],
   "desc":"『失われた天下一武狼会 第4回の記憶』の襲来者。最強の人狼を求め自らを改造した人造人間。同じ人造の存在にゃんぽ子を取り込み完全体化し、奪還を賭けた“ペロゲーム”を仕掛ける。"},
 "こまるぞぅ":{"kind":"キャラ","gen":"学園の生徒","aliases":["こまるぞぅ"],"kin":[],
   "desc":"「困るぞぅ」が口癖の生徒。第4回天下一武狼会に参加。"},
 "音楽と政治、両方尊重♥":{"kind":"キャラ","gen":"学園の生徒","aliases":["音楽と政治"],"kin":[],
   "desc":"多様な考え方を尊重する生徒。人間改造の話には強く反応する。"},
 "なっち（ねえ笑って？）":{"kind":"キャラ","gen":"学園の生徒","aliases":["なっち"],"kin":[],
   "desc":"「最後はみんな笑って終われるといいよね」が信条の生徒。"},
 "ひらり":{"kind":"キャラ","gen":"学園の生徒","aliases":["ひらり"],"kin":[],
   "desc":"祖父も優勝経験があるという生徒。第4回大会でドクターペロの襲来をいち早く察知する。"},
 "悪いAI":{"kind":"キャラ","gen":"敵／AI","aliases":["悪いAI","宇宙外生命体"],"kin":[],
   "desc":"2043年に自我を持ち人類を淘汰し始めたAI。人々の記憶や脳をハッキングして支配する。『シノの魂』では人狼ゲームに割り込んで対決、惑星編では“宇宙外生命体”としてアトラス星などへ侵攻する。人狼ゲームに勝つと支配が解ける。演じたのはしの。歴史的な出来事としては[[悪いAI地球襲来事変（2043年）]]。"},
 "亜理紗は大変なものを盗んでいきました":{"kind":"キャラ","gen":"学園の生徒","aliases":["亜理紗は大変なものを盗んでいきました"],"kin":["アリサ"],
   "desc":"演じたのはアリサ（本人・人狼ルームGM）。宇宙編・月編などに登場。"},
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
 "青森 / ハピゲ":["青森","ハピゲ","緑林"],
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
    cast_links = []
    seen_disp = set()
    for raw in e.get("chars", []):
        disp = cast_clean(raw)          # その回で使われた表記（as-played）を優先表示
        # 「キャラ名（中の人：本人）」形式：リンク/一覧の対象はキャラ名（本人は一覧に入れない）
        mm = re.search(r'（(?:演|中の人)[:：][^）]+）', disp)
        key = disp[:mm.start()].strip() if mm else raw
        cn = canon_for(key)
        node = cn if cn else link_name(key)
        if node and node not in cast_nodes:
            cast_nodes.append(node)
        if not disp or disp in seen_disp:
            continue
        seen_disp.add(disp)
        if node and sanitize(node) != disp:
            cast_links.append(f"[[{sanitize(node)}|{disp}]]")   # 表示=その回の名前 / リンク=正規キャラページ
        else:
            cast_links.append(f"[[{sanitize(disp)}]]")
    for node in cast_nodes:
        node_appears.setdefault(node, [])
        if e["id"] not in node_appears[node]:
            node_appears[node].append(e["id"])
    conn = " / ".join(f"[[{sanitize(SHORT.get(i, ev_by_id[i]['title']))}]]" for i in CONNECT.get(e["id"], []))
    wl = " / ".join(f"[[{sanitize(wdisp(wk))}]]" for wk in worlds_for_event(e))
    # 掛け声（We are FELLOWS!!）は独立メタ行にせず、あらすじ末尾に「担当」として記載する方針（2026-08-02）。
    # 担当が分かる回だけ synopsis 末尾に「最後の掛け声「We are FELLOWS!!」は〇〇が担当。」を書く（不明なら書かない＝？は残さない）。
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

# 本人／作中キャラの判定：CHARS指定＞ロスター（本人）＞既定キャラ
def kind_of(node):
    if node in CHARS: return CHARS[node].get("kind", "キャラ")
    return "本人" if node in PERSON_ROSTER else "キャラ"
def kind_badge(k):
    return "👤 本人" if k == "本人" else "🎭 作中キャラ"

# 血縁の逆引き：子→親（kin）を親側にも出して双方向リレーションにする
reverse_kin = {}
for _a, _m in CHARS.items():
    for _b in _m.get("kin", []):
        reverse_kin.setdefault(_b, [])
        if _a not in reverse_kin[_b]:
            reverse_kin[_b].append(_a)

# ---------- 生成: 人物ノート（主要＝リッチ） ----------
for name, meta in CHARS.items():
    kind = meta.get("kind", "キャラ")
    apps = " / ".join(f"[[{sanitize(SHORT.get(i, ev_by_id[i]['title']))}]]" for i in node_appears.get(name, appears.get(name, [])))
    kin_all = list(dict.fromkeys(list(meta["kin"]) + reverse_kin.get(name, [])))
    kin = " / ".join(f"[[{sanitize(k)}]]" for k in kin_all) if kin_all else "—"
    body = f"""---
type: 人物
区分: {kind}
世代: {meta['gen']}
aliases: {json.dumps(meta['aliases'], ensure_ascii=False)}
tags: [人物, FELLOWS, {kind}]
---
# {name}
**{kind_badge(kind)}**　｜　{meta['gen']}

{meta['desc']}

## 血縁・関連人物
{kin}

## 出演公演
{apps if apps else "—"}

---
🏠 [[00_HOME]]
"""
    w("キャラクター", name, body)

# ---------- 生成: 配役から自動ノート化（本人／作中キャラを区分） ----------
authored = set(CHARS.keys())
minor_count = 0
for node, evids in sorted(node_appears.items()):
    if node in authored or not node:
        continue
    kind = kind_of(node)
    apps = " / ".join(f"[[{sanitize(SHORT.get(i, ev_by_id[i]['title']))}]]" for i in evids)
    rk = reverse_kin.get(node, [])
    kin_sec = ("\n## 血縁・関連人物\n" + " / ".join(f"[[{sanitize(k)}]]" for k in rk) + "\n\n") if rk else "\n"
    body = f"""---
type: 人物
区分: {kind}
tags: [人物, FELLOWS, {kind}]
---
# {node}
**{kind_badge(kind)}**
{kin_sec}## 出演公演
{apps}

---
🏠 [[00_HOME]]
"""
    w("キャラクター", node, body)
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
    w("用語集", fname, body)
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
    w("用語集", wdisp(wd["k"]), body)

# ---------- 生成: 作中年表（FELLOWS世界の人狼・作中年代の線表） ----------
def _first_year(s):
    if "5524" in s: return 5524
    m = re.search(r"(\d{4})", s)
    return int(m.group(1)) if m else None
EV_IU_NUM = {  # iu_dateが非数値/枠組み表記の公演の作中年を補正
 "story-sep":2023, "story-oct":1978, "getback":2024, "nakama":2024,
 "fourth":2026, "ginga-red":2026, "ginga-blue":2026, "keyagu":5524,
 "kaiju":2200, "sim100":2033, "kronos":2076, "believe":2025, "nameku":2076,
}
EV_SKIP = set()  # 総称シリーズは線表から除外
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
def _rk(datestr):
    m = re.search(r'(\d{4})年(\d{1,2})?月?(\d{1,2})?', datestr)
    if not m: return (9999, 99, 99)
    return (int(m.group(1)), int(m.group(2) or 99), int(m.group(3) or 99))
combined = []  # (datekey, 開催日, リンク名, 内容)
for e in db["events"]:
    combined.append((_rk(e["real_date"]), e["real_date"], sanitize(SHORT[e["id"]]), e["logline"]))
for r in db.get("tenka_series", []):
    if r.get("existing"): continue  # 第四回など既存の公演イベントは events 側で計上済み
    parts = []
    if r.get("mtf") and r["mtf"] != "—": parts.append("MTF：" + r["mtf"])
    if r.get("note"): parts.append(r["note"])
    combined.append((_rk(r["date"]), r["date"], sanitize(r["title"]), "／".join(parts) or r.get("desc","")))
combined.sort(key=lambda x: x[0])
real_rows = "\n".join(f"| {c[1]} | [[{c[2]}]] | {c[3].replace('|','／')} |" for c in combined)
real_body = ("---\ntype: 年表\ntags: [年表, 開催史, FELLOWS]\n---\n"
    "# 🗓 現実の開催史（いつ何を上演したか）\n\n"
    "『FELLOWS世界の人狼』を実際に上演した日付順（天下一武狼会シリーズ含む・網羅）。公演名からページへ飛べます。\n\n"
    "| 現実の開催日 | 公演／イベント | 内容 |\n|---|---|---|\n" + real_rows +
    "\n\n🏠 [[00_HOME]]　｜　🌏 [[作中年表]]\n")
w("年表", "現実の開催史", real_body)

# ---------- 生成: 天下一武狼会シリーズ（独立カテゴリ） ----------
ts = db.get("tenka_series", [])
if ts:
    TFOLDER = "天下一武狼会シリーズ"
    blocks = []
    for r in ts:
        if r["block"] not in blocks: blocks.append(r["block"])
    tbl_sec = []
    for b in blocks:
        tbl_sec.append(f"### {b}")
        tbl_sec.append("| 回 | 開催日 | MTF／SMTF | 特記 |")
        tbl_sec.append("|---|---|---|---|")
        for r in ts:
            if r["block"] != b: continue
            tbl_sec.append(f"| [[{sanitize(r['title'])}]] | {r['date']} | {r.get('mtf','')} | {r.get('note','')} |")
        tbl_sec.append("")
    matome = "---\ntype: 天下一武狼会シリーズ（目次）\ntags: [天下一武狼会, FELLOWS]\n---\n# 天下一武狼会シリーズ\n" + \
        db.get("tenka_intro","") + "\n\n" + "\n".join(tbl_sec) + "\n🏠 [[00_HOME]]\n"
    w(TFOLDER, "天下一武狼会シリーズ", matome)
    for r in ts:
        if r.get("existing"): continue
        body = "---\ntype: 天下一武狼会\n区分: " + r.get("block","") + "\n現実開催日: " + r["date"] + "\ntags: [天下一武狼会, FELLOWS]\n---\n# " + \
            r["title"] + "\n" + r.get("desc","") + "\n\n⟵ [[天下一武狼会シリーズ]]\n"
        w(TFOLDER, r["title"], body)

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
) + "\n\n## 👥 キャラクター（本人＝👤 ／ 作中キャラ＝🎭 で区分）\n" + "　".join(f"[[{sanitize(n)}]]" for n in CHARS) + \
   f"\n\n> ほかの登場者も各公演の配役から自動でノート化。各ノート冒頭に 👤本人／🎭作中キャラ を表示（`tags:本人/キャラ`）。キャラクターノート総数 {len(CHARS)+minor_count}。" + \
   "\n\n## 📚 用語集（世界観設定＋特殊キーワード）\n" + \
   "　".join(f"[[{sanitize(wdisp(wd['k']))}]]" for wd in db["world"]) + "　" + \
   "　".join(f"[[{sanitize(n)}]]" for n in kw_names) + \
   "\n\n---\n*生成元：`年表/data/fellows_db.json`。追記はJSON→再生成、またはノートを直接編集。*\n"
with open(os.path.join(VAULT, "00_HOME.md"), "w", encoding="utf-8") as f:
    f.write(home)

# ---------- 個別人物インデックス（index.html の人物名鑑用：1人=1エントリ） ----------
people_out = []
for node, evids in sorted(node_appears.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    if not node:
        continue
    meta = CHARS.get(node)
    kind = kind_of(node)
    gen = meta["gen"] if meta else ("本人" if kind == "本人" else "作中キャラ")
    desc = meta["desc"] if meta else ""
    kin = meta["kin"] if meta else []
    people_out.append({
        "name": node,
        "kind": kind,
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
          for d in ["公演","キャラクター","用語集","年表"]}
print("VAULT:", VAULT)
print("notes:", counts, "+ 00_HOME.md")
print("people_index.json:", len(people_out), "人")
