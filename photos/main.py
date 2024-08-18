import os
import sys
from datetime import datetime
from typing import Optional, Any
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
import rawpy
from pillow_heif import register_heif_opener

# Register HEIF opener
register_heif_opener()


def get_date_taken(image_path: str) -> datetime:
    file_extension: str = os.path.splitext(image_path)[1].lower()

    if file_extension in [".arw"]:  # Sony RAW
        try:
            with rawpy.imread(image_path) as raw:
                exif: dict[str, Any] = raw.raw_metadata
                date_str_raw: Optional[bytes] = exif.get(
                    "DateTimeOriginal"
                ) or exif.get("DateTime")
                if date_str_raw:
                    return datetime.strptime(date_str_raw.decode(), "%Y:%m:%d %H:%M:%S")
        except Exception as e:
            print(f"Error reading RAW data from {image_path}: {e}")
    else:  # For other formats (JPEG, HEIC, PNG, etc.)
        try:
            with Image.open(image_path) as img:
                exf: Image.Exif = img.getexif()
                date_str_img: Optional[str] = exf.get(36867) or exf.get(
                    306
                )  # 36867 is DateTimeOriginal, 306 is DateTime
                if date_str_img:
                    return datetime.strptime(date_str_img, "%Y:%m:%d %H:%M:%S")
        except Exception as e:
            print(f"Error reading EXIF data from {image_path}: {e}")

    # If EXIF data is not available, use file modification time
    return datetime.fromtimestamp(os.path.getmtime(image_path))


def organize_images(source_folder: str, target_folder: str) -> None:
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for filename in os.listdir(source_folder):
        file_path: str = os.path.join(source_folder, filename)
        if os.path.isfile(file_path):
            date_taken: datetime = get_date_taken(file_path)
            year_folder: str = os.path.join(target_folder, str(date_taken.year))
            date_folder: str = os.path.join(
                year_folder, date_taken.strftime("%Y-%m-%d")
            )

            os.makedirs(year_folder, exist_ok=True)
            os.makedirs(date_folder, exist_ok=True)

            new_file_path: str = os.path.join(date_folder, filename)

            if os.path.exists(new_file_path):
                print(f"File {filename} already exists in {date_folder}. Skipping.")
            else:
                shutil.copy2(file_path, new_file_path)
                print(f"Copied {filename} to {new_file_path}")


def main():
    if len(sys.argv) != 3:
        print("Usage: poetry run photos <source_folder> <target_folder>")
        sys.exit(1)

    source_folder: str = sys.argv[1]
    target_folder: str = sys.argv[2]

    organize_images(source_folder, target_folder)


if __name__ == "__main__":
    main()
