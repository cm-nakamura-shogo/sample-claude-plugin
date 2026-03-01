---
name: profile-photo-processor
description: プロフィール写真を標準化します。人物切り出し、背景をグレー(#e1e1e1)に置換、顔位置・サイズを統一します。Docker環境で実行します。
---

# Profile Photo Processor

プロフィール写真を標準化するスキルです。

## 処理内容

- 人物を切り出し、背景を #e1e1e1（グレー）に置換
- 顔の位置を画像上部30%に統一
- 顔のサイズを画像高さの18%に統一
- 出力サイズ: 2160 x 3840 px

## 実行手順

### 1. Docker環境の確認

まずユーザーのDocker環境を確認してください：

```bash
docker --version
```

**Dockerがない場合は以下を案内してください：**

> Dockerがインストールされていません。以下のいずれかをインストールしてください：
>
> - **Rancher Desktop**（推奨）: https://rancherdesktop.io/
>   - 無料で商用利用可能
>   - インストール後、Container Engineを「dockerd (moby)」に設定
>
> - **Docker Desktop**: https://www.docker.com/products/docker-desktop/
>   - 個人利用は無料
>
> - **Podman**: https://podman.io/
>   - 完全無料のオープンソース
>
> インストール完了後、再度このスキルを実行してください。

Dockerがインストールされていても起動していない場合：
```bash
docker ps
```
で接続エラーが出たら、Docker/Rancher Desktopを起動するよう案内してください。

### 2. ユーザーへの確認（必須）

**処理実行前に必ず以下をユーザーに確認してください：**

1. 入力ファイル/フォルダのパス
2. 出力先のパス
3. フォルダの場合は処理対象ファイル数

以下の形式で確認してください：

```
以下の内容でプロフィール写真を処理します：

- 入力: [入力パス]
- 出力: [出力パス]
- 処理対象: [ファイル数]枚

処理内容：
- 背景を #e1e1e1 に置換
- 顔の位置・サイズを標準化
- 出力サイズ: 2160 x 3840 px

実行してよろしいですか？
```

ユーザーの承認を得てから次に進んでください。

### 3. Dockerイメージのビルド

このスキルのディレクトリ（Dockerfileがある場所）でイメージをビルドします：

```bash
docker build -t profile-photo-processor .
```

初回は背景除去AIモデル（約170MB）のダウンロードがあるため数分かかります。

### 4. 画像処理の実行

**単一ファイルの場合：**

```bash
docker run --rm \
  -v "[入力ファイルの親ディレクトリ]:/input:ro" \
  -v "[出力ディレクトリ]:/output" \
  profile-photo-processor \
  /input/[ファイル名] /output/[出力ファイル名]
```

**フォルダ一括処理の場合：**

```bash
docker run --rm \
  -v "[入力フォルダ]:/input:ro" \
  -v "[出力フォルダ]:/output" \
  profile-photo-processor \
  /input /output
```

### 5. 処理結果の確認

処理完了後、出力された画像をユーザーに確認してもらいます。

## オプション

| パラメータ | 説明 | デフォルト |
|-----------|------|-----------|
| `--extensions` | 処理対象の拡張子（カンマ区切り） | `jpg,jpeg,png,webp` |

## エラー対処

### "Cannot connect to the Docker daemon"
Docker/Rancher Desktopが起動していることを確認してください。

### "No face detected"
顔が検出されない場合は画像中心を基準に処理します。正面向きの写真を推奨してください。

### "Permission denied"
出力フォルダへの書き込み権限を確認してください。
