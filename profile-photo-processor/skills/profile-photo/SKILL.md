---
name: profile-photo-processor
description: プロフィール写真の標準化処理。
背景除去、顔センタリング、明るさ補正を自動で行う。
Dockerで実行するため安全。
---

# Profile Photo Processor

プロフィール写真を標準化するスキルです。以下の処理を自動で行います：

- 背景除去（人物のみを切り出し、滑らかなエッジ処理）
- 背景色を #e1e1e1（グレー）に統一
- 顔の位置を画像上部38%に配置
- 顔のサイズを統一（画像高さの約18%）
- 出力サイズ: 810x1440px

## 前提条件

このスキルはDockerコンテナ内で実行されます。

**必要な環境:**
- Docker または Docker互換のコンテナランタイム（Rancher Desktop、Podman等）

## 実行手順

### 1. Docker環境の確認

まず、ユーザーがDocker環境を持っているか確認してください：

```bash
docker --version
```

**Dockerがインストールされていない場合:**

以下のいずれかをインストールするようユーザーに案内してください：

- **Rancher Desktop** (推奨): https://rancherdesktop.io/
  - macOS/Windows/Linux対応
  - 無料で商用利用可能
  - インストール後、Container Engineを「dockerd (moby)」に設定

- **Docker Desktop**: https://www.docker.com/products/docker-desktop/
  - 個人利用は無料、商用は有料の場合あり

- **Podman**: https://podman.io/
  - 完全無料のオープンソース
  - `podman` コマンドを `docker` のエイリアスとして設定

### 2. ユーザー確認

**重要:** 処理を実行する前に、必ず以下の情報をユーザーに確認してください：

1. **処理対象の確認**
   - 入力ファイル/フォルダのパス
   - 出力先のパス
   - 処理対象ファイル数（フォルダの場合）

2. **処理内容の説明**
   - 背景が #e1e1e1 のグレーに置き換わること
   - 顔の位置とサイズが標準化されること
   - 出力形式はJPEG（品質95%）

3. **確認メッセージの例:**

```
以下の内容でプロフィール写真を処理します：

入力: /path/to/input/photos/
出力: /path/to/output/
処理対象: 5枚の画像ファイル

処理内容:
- 背景を #e1e1e1 に置換
- 顔の位置・サイズを標準化
- 出力サイズ: 810x1440px

実行してよろしいですか？
```

### 3. Dockerイメージのビルド

スキルのディレクトリを確認し、イメージをビルドします：

```bash
# スキルディレクトリに移動
cd <SKILL_DIRECTORY>

# Dockerイメージをビルド（初回のみ、または更新時）
docker build -t profile-photo-processor .
```

**注意:** 初回ビルド時はAIモデル（約170MB）のダウンロードがあるため、数分かかります。

### 4. 画像処理の実行

**単一ファイルの処理:**

```bash
docker run --rm \
  -v "/path/to/input:/input:ro" \
  -v "/path/to/output:/output" \
  profile-photo-processor \
  /input/photo.jpg /output/photo_processed.jpg
```

**フォルダ内の全画像を処理:**

```bash
docker run --rm \
  -v "/path/to/input/folder:/input:ro" \
  -v "/path/to/output/folder:/output" \
  profile-photo-processor \
  /input /output
```

### 5. 処理結果の確認

処理完了後、出力フォルダの画像をユーザーに確認してもらいます。

## パラメータ

| パラメータ | 説明 | デフォルト |
|-----------|------|-----------|
| `--extensions` | 処理対象の拡張子（カンマ区切り） | `jpg,jpeg,png,webp` |

## エラー対処

### よくあるエラー

1. **"Cannot connect to the Docker daemon"**
   - Docker/Rancher Desktopが起動していることを確認
   - `docker ps` で接続確認

2. **"No face detected"**
   - 顔が正面を向いていない可能性
   - 画像が暗すぎる/明るすぎる可能性
   - → 画像中央を基準に処理は継続されます

3. **"Permission denied"**
   - 出力フォルダへの書き込み権限を確認

## 技術仕様

- **背景除去:** rembg (isnet-general-use モデル + post_process_mask)
- **顔検出:** OpenCV Haar Cascade
- **出力サイズ:** 810 x 1440 px
- **顔位置:** 上端から38%
- **顔サイズ:** 画像高さの約18%
- **背景色:** #e1e1e1 (RGB: 225, 225, 225)
- **出力形式:** JPEG (品質95%)
