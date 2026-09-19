# JR-100 開発指針

- 依頼範囲の実装・検証まで完了する。可逆的なローカル作業は進め、目的・範囲・重要な制約の変更は確認する。
- CPUはMB8861H（6800系＋独自拡張）。MC6809命令は禁止。CPU・I/O変更時は `rules/hardware.md` と `rules/assembly.md` を参照する。
- 公開ゲームは標準RAM 16KB、32×24文字、PCG 32文字、単音。作業領域・画面バッファ・スタックもRAMに収める。
- ゲーム開発は `games/README.md`、操作説明はタイトル・ヘルプにまとめ、本編は盤面と判断材料に集中させる。演出は `docs/game-presentation.md`、ツールチェーンは `docs/README.md` を必要時に参照する。
- 新規の Python ゲームは `docs/python-games/README.md` と `language.md` を読み、`games/dev.py init` で初期化する。検証・撮影・配布は `dev.py test` / `release` を使い、失敗時は JSON 診断とログから元ソースを修正する。既存作品の移行は依頼がある場合に限る。
- `src/jr100dev/asm/opcodes_mb8861h.py` は手編集せず、`tools/sync_opcodes.py` で生成する。
- 検証は変更範囲に合わせ、ゲームは `make -C games/<directory> test`、ツールは `.venv/bin/python -m pytest <test-path>`。理由のない全件実行・反復は不要。
- 静的検査・エミュレーター動作・実機確認を区別し、未確認を合格扱いしない。
- 公開時は `games/media/README.md` を参照し、PRG・画像・動画・Wikiの公開URLを確認する。ROM・秘密情報・私的資料は含めない。
