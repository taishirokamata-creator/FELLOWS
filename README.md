# FELLOWS貸切 / フェローズ学園 年表

人狼ルーム「FELLOWS貸切」のストーリー人狼と、近未来SF「フェローズ学園」の
公演史・作中年表・人物名鑑・世界観・用語をまとめた自己完結型のWebサイトです。

- `index.html` … 年表サイト本体（外部依存なし・これ単体で動きます）
- `data/fellows_db.json` … 一次データ（公演・人物・世界観・キーワード・調べるリスト）

## 公開（GitHub Pages）

1. GitHubで新規リポジトリを作成（例: `fellows-nenpyo`）
2. このフォルダ（`index.html` がある階層）を push
3. リポジトリの **Settings → Pages → Build and deployment** で
   Source を「Deploy from a branch」、Branch を `main` / `(root)` に設定
4. 数分後、`https://<ユーザー名>.github.io/<リポジトリ名>/` で公開されます

## 更新

`data/fellows_db.json` を編集 → `index.html` を再生成（埋め込みデータを差し替え）→ commit & push。

---
※本サイトの物語・シナリオはFELLOWS貸切主催 しのぴ 氏の創作を含みます。公開時はご配慮ください。
