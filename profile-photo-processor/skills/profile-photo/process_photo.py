#!/usr/bin/env python3
"""
Profile Photo Processor
- Remove background and replace with #e1e1e1
- Detect face and standardize position
- Output standardized profile photos
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session

# Constants
BACKGROUND_COLOR = (225, 225, 225)  # #e1e1e1
OUTPUT_WIDTH = 810
OUTPUT_HEIGHT = 1440
FACE_POSITION_RATIO = 0.38  # Face center at 38% from top


def detect_face(image_np: np.ndarray) -> tuple[int, int, int, int] | None:
    """Detect face using OpenCV's Haar Cascade classifier."""
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

    # Load face cascade
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)
    )

    if len(faces) == 0:
        return None

    # Return the largest face
    largest_face = max(faces, key=lambda f: f[2] * f[3])
    return tuple(largest_face)


def process_image(input_path: str, output_path: str, session) -> bool:
    """Process a single image."""
    try:
        # Load image
        with open(input_path, 'rb') as f:
            input_data = f.read()

        # Remove background with post-processing for smoother edges
        output_data = remove(
            input_data,
            session=session,
            post_process_mask=True,
        )
        img = Image.open(__import__('io').BytesIO(output_data)).convert('RGBA')

        # Convert to numpy for face detection
        img_np = np.array(img)
        rgb_for_detection = img_np[:, :, :3]

        # Detect face
        face = detect_face(rgb_for_detection)

        if face is None:
            print(f"Warning: No face detected in {input_path}, using center positioning")
            # Use image center as fallback
            face_center_y = img.height // 2
            face_height = img.height // 4
        else:
            x, y, w, h = face
            face_center_y = y + h // 2
            face_height = h

        # Calculate scaling to achieve standard face size
        # Target face height should be about 18% of output height
        target_face_height = OUTPUT_HEIGHT * 0.18
        scale = target_face_height / face_height

        # Scale the image
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        img_scaled = img.resize((new_width, new_height), Image.LANCZOS)

        # Calculate position to place face at target position
        scaled_face_center_y = int(face_center_y * scale)
        target_face_y = int(OUTPUT_HEIGHT * FACE_POSITION_RATIO)

        # Calculate paste position
        paste_y = target_face_y - scaled_face_center_y
        paste_x = (OUTPUT_WIDTH - new_width) // 2

        # Create output image with background color
        output_img = Image.new('RGB', (OUTPUT_WIDTH, OUTPUT_HEIGHT), BACKGROUND_COLOR)

        # Paste the processed image
        output_img.paste(img_scaled, (paste_x, paste_y), img_scaled)

        # Save output
        output_img.save(output_path, 'JPEG', quality=95)

        return True

    except Exception as e:
        print(f"Error processing {input_path}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='Process profile photos')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('output', help='Output file or directory')
    parser.add_argument('--extensions', default='jpg,jpeg,png,webp',
                        help='Comma-separated list of file extensions to process')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    extensions = set(ext.lower().strip() for ext in args.extensions.split(','))

    # Initialize rembg session with isnet-general-use model for better edge quality
    session = new_session('isnet-general-use')

    if input_path.is_file():
        # Single file processing
        if output_path.is_dir():
            output_file = output_path / f"{input_path.stem}_processed.jpg"
        else:
            output_file = output_path

        output_file.parent.mkdir(parents=True, exist_ok=True)

        if process_image(str(input_path), str(output_file), session):
            print(f"Processed: {input_path} -> {output_file}")
        else:
            sys.exit(1)

    elif input_path.is_dir():
        # Directory processing
        output_path.mkdir(parents=True, exist_ok=True)

        success_count = 0
        fail_count = 0

        for file_path in input_path.iterdir():
            if file_path.suffix.lower().lstrip('.') in extensions:
                output_file = output_path / f"{file_path.stem}_processed.jpg"

                if process_image(str(file_path), str(output_file), session):
                    print(f"Processed: {file_path.name} -> {output_file.name}")
                    success_count += 1
                else:
                    fail_count += 1

        print(f"\nCompleted: {success_count} succeeded, {fail_count} failed")

        if fail_count > 0:
            sys.exit(1)
    else:
        print(f"Error: Input path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
