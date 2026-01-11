#!/usr/bin/env python3
"""
Profile Photo Processor

プロフィール写真を標準化するスクリプト:
- 人物を切り出し、背景を #e1e1e1 に置換
- 顔の位置とサイズを統一
"""

import argparse
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session

# 定数
BACKGROUND_COLOR = (225, 225, 225)  # #e1e1e1
OUTPUT_WIDTH = 2160
OUTPUT_HEIGHT = 3840
FACE_POSITION_RATIO = 0.30  # 顔の中心を上から30%の位置に配置
TARGET_FACE_RATIO = 0.18  # 顔サイズを画像高さの18%に統一


def detect_face(image_np: np.ndarray) -> tuple[int, int, int, int] | None:
    """OpenCVのHaar Cascadeで顔を検出"""
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100)
    )

    if len(faces) == 0:
        return None

    # 最大の顔を返す
    largest = max(faces, key=lambda f: f[2] * f[3])
    return tuple(largest)


def process_single_image(input_path: str, output_path: str, session) -> bool:
    """単一画像を処理"""
    try:
        print(f"処理中: {input_path}")

        # 画像読み込み
        with open(input_path, 'rb') as f:
            input_data = f.read()

        # 背景除去
        output_data = remove(
            input_data,
            session=session,
            post_process_mask=True,
        )
        img_rgba = Image.open(io.BytesIO(output_data)).convert('RGBA')

        # 顔検出用にRGBに変換
        img_rgb = img_rgba.convert('RGB')
        img_np = np.array(img_rgb)

        face = detect_face(img_np)

        if face is None:
            print(f"  警告: 顔が検出されませんでした。画像中心を基準に処理します。")
            face_center_y = img_rgba.height // 2
            face_height = img_rgba.height // 5
            face_center_x = img_rgba.width // 2
        else:
            x, y, w, h = face
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            face_height = h
            print(f"  顔検出: 位置({x}, {y}), サイズ({w}x{h})")

        # スケール計算（顔サイズを統一）
        target_face_height = OUTPUT_HEIGHT * TARGET_FACE_RATIO
        scale = target_face_height / face_height

        # 画像をスケーリング
        new_width = int(img_rgba.width * scale)
        new_height = int(img_rgba.height * scale)
        img_scaled = img_rgba.resize((new_width, new_height), Image.LANCZOS)

        # 顔位置を計算
        scaled_face_center_y = int(face_center_y * scale)
        scaled_face_center_x = int(face_center_x * scale)
        target_face_y = int(OUTPUT_HEIGHT * FACE_POSITION_RATIO)

        # 配置位置を計算
        paste_y = target_face_y - scaled_face_center_y
        paste_x = (OUTPUT_WIDTH - new_width) // 2  # 水平方向は中央配置

        # 背景画像を作成
        output_img = Image.new('RGBA', (OUTPUT_WIDTH, OUTPUT_HEIGHT), (*BACKGROUND_COLOR, 255))

        # 人物を配置
        output_img.paste(img_scaled, (paste_x, paste_y), img_scaled)

        # RGBに変換して保存
        output_rgb = output_img.convert('RGB')

        # 保存
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        output_rgb.save(output_path, 'JPEG', quality=95)

        print(f"  完了: {output_path}")
        return True

    except Exception as e:
        print(f"  エラー: {e}", file=sys.stderr)
        return False


def process_directory(input_dir: str, output_dir: str, extensions: set, session) -> tuple[int, int]:
    """ディレクトリ内の画像を一括処理"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = 0

    for file in input_path.iterdir():
        if file.is_file() and file.suffix.lower().lstrip('.') in extensions:
            out_file = output_path / f"{file.stem}_processed.jpg"
            if process_single_image(str(file), str(out_file), session):
                success += 1
            else:
                failed += 1

    return success, failed


def main():
    parser = argparse.ArgumentParser(
        description='プロフィール写真を標準化します'
    )
    parser.add_argument('input', help='入力ファイルまたはディレクトリ')
    parser.add_argument('output', help='出力ファイルまたはディレクトリ')
    parser.add_argument(
        '--extensions',
        default='jpg,jpeg,png,webp',
        help='処理対象の拡張子（カンマ区切り）'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    extensions = set(ext.lower().strip() for ext in args.extensions.split(','))

    # rembgセッションを初期化
    print("背景除去モデルを初期化中...")
    session = new_session('isnet-general-use')
    print("初期化完了\n")

    if input_path.is_file():
        # 単一ファイル処理
        if output_path.is_dir():
            out_file = output_path / f"{input_path.stem}_processed.jpg"
        else:
            out_file = output_path

        if process_single_image(str(input_path), str(out_file), session):
            print("\n処理が完了しました。")
        else:
            sys.exit(1)

    elif input_path.is_dir():
        # ディレクトリ処理
        success, failed = process_directory(
            str(input_path), str(output_path), extensions, session
        )
        print(f"\n処理完了: 成功 {success}件, 失敗 {failed}件")
        if failed > 0:
            sys.exit(1)
    else:
        print(f"エラー: 入力パスが存在しません: {input_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
