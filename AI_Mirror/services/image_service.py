import shutil
import uuid
from pathlib import Path

import cv2

from paths import (
    PROJECT_ROOT,
    SHIRT_IMAGE_DIR,
    PANTS_IMAGE_DIR,
)


ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
}


class ImageService:
    def save_product_image(
        self,
        source_path: str,
        tryon_category: str
    ) -> str:
        source = Path(source_path)

        if not source.exists():
            raise FileNotFoundError(
                "Selected image does not exist."
            )

        extension = source.suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported image format."
            )

        image = cv2.imread(str(source), cv2.IMREAD_UNCHANGED)

        if image is None:
            raise ValueError(
                "The selected file is not a valid image."
            )

        if tryon_category == "Shirts":
            destination_dir = SHIRT_IMAGE_DIR

        elif tryon_category == "Pants":
            destination_dir = PANTS_IMAGE_DIR

        else:
            destination_dir = PROJECT_ROOT / "img" / "other"

        destination_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = f"{uuid.uuid4().hex}{extension}"
        destination = destination_dir / filename

        shutil.copy2(source, destination)

        return destination.relative_to(
            PROJECT_ROOT
        ).as_posix()

    def delete_product_image(
        self,
        relative_path: str
    ) -> bool:
        if not relative_path:
            return False

        image_path = PROJECT_ROOT / relative_path

        if not image_path.exists():
            return False

        image_path.unlink()
        return True