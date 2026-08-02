# FELLOWS 年表・Wiki プロジェクト 引継ぎ書（新PC移行用）

人狼コミュニティ「FELLOWS貸切」のストーリー人狼と、近未来SF「FELLOWS学園」の
**年表・設定データベース**を作るプロジェクト。趣味プロジェクト（会計業務とは無関係）。

最終更新：2026-07-26

---

## 0. 一番大事なこと（移行時の要点）

- **プロジェクト本体は Google Drive の `マイドライブ/FELLOWS/` にある**ので、新PCで
  Google Drive デスクトップを同じアカウントで同期すれば**ファイルは自動で揃う**。
- **ビルドスクリプトは以前 Claude の一時フォルダ(scratchpad)にしか無く、消える危険があった**。
  → 今回 `年表/build/` に移設し、**パスを自動計算（可搬）**にした。もうPCが変わっても動く。
- 新PCで必要なのは **Python** と **Git** と **Google Drive 同期**、そして続きをやるなら **Claude Code** だけ。

---

## 1. 成果物と公開URL

| 種類 | URL / 場所 | 中身 |
|---|---|---|
| 🐺 年表サイト（公開） | https://taishirokamata-creator.github.io/FELLOWS/ | 5タブ年表。人物105を1人1カード＋検索＋クリック詳細 |
| 📚 用語Wiki（公開） | https://taishirokamata-creator.github.io/FELLOWS/wiki.html | Wikipedia風 172ページ。スマホは「☰ 目次」で開閉 |
| 年表（限定共有・非公開） | Claude Artifact `5674cfb9-ee40-4436-9628-b0cbfc75fa63` | GitHub版と同じ。内輪限定で配りたい時用 |
| Wiki（限定共有・非公開） | Claude Artifact `ca904966-7ce4-45e2-b3ba-fc1d1f606a75` | 同上 |

- GitHub Pages は**完全公開**（URLを知れば誰でも・ログイン不要）。限定公開したいときは Artifact版を使う。
- GitHub リポジトリ：`taishirokamata-creator/FELLOWS`（**大文字**）。`年表/` フォルダが git のルート。

---

## 2. フォルダ構成

```
マイドライブ/FELLOWS/
├── 過去データ/                     … 公演ごとのPDF/Word台本（一次資料）。フォルダ名=「YYYY.MM.DD タイトル」
│   └── _重複_旧版_削除可/          … 重複の旧版を退避（承認あれば削除可）
├── FELLOWS_Vault/                  … Obsidian金庫（自動生成物。手で編集しない）
│   ├── 公演/ 人物/ 設定/ キーワード/ 年表/ 00_HOME.md
└── 年表/                          ← ここが git ルート（GitHub Pages 公開対象）
    ├── index.html                 … 年表サイト本体（DATA と PEOPLE を埋め込み済みの自己完結HTML）
    ├── wiki.html                  … 用語Wiki本体（自己完結HTML）
    ├── HANDOFF.md                 … この引継ぎ書
    ├── README.md / .nojekyll / .gitignore
    ├── data/
    │   ├── fellows_db.json         ★★ 一次データ＝すべての正（single source of truth）
    │   └── people_index.json       … 個別人物105人の索引（build_vault.py が自動生成）
    ├── build/                      … ビルドスクリプト一式（← 今回ここに集約）
    │   ├── build_all.py            … ★ワンコマンド一括ビルド
    │   ├── build_vault.py          … fellows_db.json → Obsidian金庫 ＋ people_index.json
    │   ├── build_wiki.py           … Obsidian金庫 → wiki.html
    │   ├── reinject_index.py       … fellows_db.json / people_index.json → index.html へ再注入
    │   ├── make_artifact_sources.py… index/wiki → Artifact用ソース(_*.html)を生成
    │   └── render_pdf.py           … 文字化けPDFを画像化する補助
    ├── _artifact_source.html       … Artifact年表版ソース（.gitignoreで除外・生成物）
    └── _wiki_artifact.html         … Artifact Wiki版ソース（.gitignoreで除外・生成物）
```

---

## 3. データの流れ（アーキテクチャ）

**`data/fellows_db.json` が唯一の正。** ここを直して再ビルドすれば全部が作り直される。

```
data/fellows_db.json  ──┬─→ build_vault.py ─→ FELLOWS_Vault/（Obsidian金庫）＋ data/people_index.json
                        │                          │
                        │                          └─→ build_wiki.py ─→ wiki.html
                        │
                        └─→ reinject_index.py ─→ index.html（DATA と PEOPLE を埋め込み）
                                                   │
                        make_artifact_sources.py ─┴→ _artifact_source.html / _wiki_artifact.html
```

`build/build_all.py` がこの順番を全部やってくれる。

### fellows_db.json の構造（主なキー）
- `canon[]` … 正史の大年表（年・タイトル・detail・tag）
- `events[]` … 公演（id / title / series / real_date / iu_date / logline / synopsis / chars[] / world[] / connects[]）
- `chars[]` … 人物名鑑の「まとめ」記述（世代グループ単位）※個別105人は people_index.json 側
- `world[]` … 世界観設定（k / v）
- `keywords[]` … 特殊用語（k / v / see[]）
- `open_questions[]` … 未確定・要確認リスト（Wikiの「調べるリスト」になる）

### build_vault.py 内の重要な辞書（新公演・新キャラを足すとき触る）
- `SHORT` … event id → 短縮タイトル
- `CONNECT` … event id → 関連 event id[]（金庫の「つながり」）
- `STORY_ORDER` … 作中年代順の並び
- `CHARS` … 主要人物の正規名・エイリアス・血縁・説明（リッチな人物ノートの元）
  - `canon_for()` が配役表記を CHARS のエイリアスで正規名へ寄せる
  - CHARS に無い配役は「端役/脇役」ノートを自動生成
- 参考：index.html 側にも作中順の `ORDER` 配列がある（新公演を足したらここにも id を追加）

---

## 4. 新PCセットアップ手順

1. **Google Drive デスクトップ** を同じGoogleアカウントで入れて `マイドライブ/FELLOWS` を同期。
   - ※ドライブ文字やユーザー名が変わっても、ビルドスクリプトは自分の位置から相対でパスを出すのでOK。
2. **Python 3.x** を入れる（`python --version` で確認）。
3. ライブラリ：`pip install pymupdf`（`render_pdf.py` 用。ビルド自体は標準ライブラリのみで動く）。
4. **Git** を入れ、GitHub にログインできるようにする（初回 push 時に認証）。
   - リポジトリはクローン済みの実体が `年表/` にある（`git remote -v` で `taishirokamata-creator/FELLOWS` を確認）。
   - もし新PCで git 履歴が無ければ、`年表/` で改めて `git clone` するか、既存 `.git` ごと同期されていればそのまま使える。
   - commit の名前/メールが未設定なら：`git config user.email "taishiro.kamata@kamatacpa.com"` / `git config user.name "Taishiro Kamata"`
5. 続きの制作を Claude にやってもらうなら **Claude Code** を入れ、この `HANDOFF.md` を読ませる。

### 動作確認
```
cd "（各自の）マイドライブ/FELLOWS/年表"
python build/build_all.py
```
→ 金庫・wiki.html・index.html・Artifactソースが再生成されれば移行成功。

---

## 5. 日常の更新ワークフロー

### A. 新しい公演／キャラ／設定を足す
1. `data/fellows_db.json` に追記（events / chars / keywords / open_questions）。
2. 新公演なら `build/build_vault.py` の `SHORT` `CONNECT` `STORY_ORDER`、必要なら `index.html` の `ORDER` にも id を追加。
   主要キャラを足すなら `build_vault.py` の `CHARS` に追記。
3. 一括ビルド：`python build/build_all.py`
4. ブラウザで `年表/index.html`・`年表/wiki.html` を開いて確認。
5. GitHubへ反映：`年表/` で
   ```
   git add -A
   git commit -m "内容"
   git push
   ```
   ※PowerShellでは `&&` が使えない。`git add -A` → Enter → `git commit ...` → Enter → `git push` と1行ずつ。
6. 30秒〜1分で GitHub Pages に反映。
7. （任意）限定共有Artifactも更新したいときは、Claude に「_artifact_source.html と _wiki_artifact.html を
   既存URLへ再Publishして」と頼む（URLは §1 の Artifact ID）。

### B. 台本PDFを読む（文字化け対策）
- 普通のPDF/Wordは Claude がそのまま読める。
- **フォント埋め込みでテキストが文字化けするPDF**（例：ナメック星へ）は画像化する：
  ```
  python build/render_pdf.py "過去データ/○○/台本.pdf" 150
  ```
  → `台本_img/p01.png…` ができるので、それを Claude に読ませる。

---

## 6. 正史のあらすじ（背景知識）

2013 人狼ルーム → 2021 FELLOWS貸切誕生 → 2020年代 AI成長/スイーツ派 → 2034 人間しのぴ死 →
2043 悪いAI戦争＆学園設立 → 2070 ギャラガーAI完成 → 2073-2076 学園編（惑星巡り）→
超未来5524年（This is history / ケヤグセカイ）。**学園長しのぴはAI**、ギャラガーもAI。
作中の「現在」は正典で **2076年**。

**本命アーカイブ**：Google Drive 共有フォルダ「FELLOWS世界の人狼」
(id=`155KtZy8M6zSzq1WCtEULIOaV2jP5xrjP`、所有 sabo1069) が最も網羅的。
制作者の正典＝そのフォルダ内「歴史/FELLOWS学園_世界観・事前共有.pdf」
(id=`1kxQ4sOYbRmJ-BAXlZOc4Ej5QOriYbiTi`)。
※Claudeの Google Drive 連携は `parentId` 検索が空を返すことがあるが、**ファイルIDを直接指定すれば
`read_file_content` で読める**。フォルダIDはChromeで開いてタブURLから取得。

---

## 7. 未解決事項（調べるリスト）

主催 **しのぴ（X: @sea_now13）** に聞くか、詳しい人に確認する。分かり次第 `fellows_db.json` に反映。

- 開催日が未確定：フェロウズ未来へ / NEVER!NEVER!NEVER! / オープン・ザ・アイズ /
  NAOKI EMPIRE INVASION(本体) / ラストクリスマスの逆襲(本編) / FELLOWS学園Z / 怪獣 / 天下一武狼会(初回)
- 「失われた天下一武狼会 第4回」(2026/05/04) と「なぞの四人目の男」(2026/05/04) は同日。昼夜2部制か別日か、通し回数。
- NAOKI CLOSE(2026.02.04 第60回) と NAOKI EMPIRE INVASION は別イベントか。
- 人間しのぴの死亡年：『シノの魂』=2033年 / 正典・『未来へ』=2034年 のどちらが正か。
- 銀河鉄道の夜 青 の通し回数（Xの投稿では72だが前後と不整合）。

**Xでの開催日調べ方**：告知は「YYYYMMDD FELLOWS [ローマ数字回] タイトル」形式。
イベント名でピンポイント検索（例 `from:sea_now13 ナメック`）が速い。#しのろう は雑多。

---

## 8. 注意点

- **Obsidian金庫・wiki.html・index.html・people_index.json は全部“生成物”**。手で直しても次のビルドで消える。
  直すのは必ず `data/fellows_db.json`（と、構造を変えるなら `build/` の各スクリプト）。
- Google Drive 共有ドライブをChromeで辿ると「共有アイテム」に**本人の機微な業務ファイル**（税務書類の写真等）が
  混ざることがある。無闇に広域検索しない。過去データ内に紛れ込んだ請求書PDF等は開かない。
- `git remote add` / `git push` は Claude の安全機構でブロックされることがある。その場合は**人間が実行**する
  （commit まではClaudeが可）。
