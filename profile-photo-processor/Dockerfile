FROM python:3.11-slim

WORKDIR /app

# OpenCV と rembg に必要なシステム依存関係をインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# rembgモデルを事前ダウンロード（実行時のダウンロードを回避）
RUN python -c "from rembg import new_session; new_session('isnet-general-use')"

# 処理スクリプトをコピー
COPY process_photo.py .

ENTRYPOINT ["python", "process_photo.py"]
