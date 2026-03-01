---
description: PDFの指定ページを抽出する
---

$ARGUMENTS を元に指定されたページをまず抽出します。以下がコマンドの例です。

```
uv run ~/.claude/scripts/extract_pdf_pages.py input.pdf output.pdf 260 5
```

260は抽出開始ページ、5は抽出ページ数です。

次に出力されたoutput.pdfを、claude codeで読み込みます。

読み込んだ結果をユーザに返しましょう。ユーザから質問がある場合はそれに回答してください。
