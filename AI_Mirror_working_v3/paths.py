from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
CATALOGUE_PATH = DATA_DIR / "catalogue.json"
STORE_MAP_PATH = DATA_DIR / "store_map.json"

IMAGE_DIR = PROJECT_ROOT / "img"
SHIRT_IMAGE_DIR = IMAGE_DIR / "shirts"
PANTS_IMAGE_DIR = IMAGE_DIR / "pants"

ASSETS_DIR = PROJECT_ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
MAPS_DIR = ASSETS_DIR / "maps"
PLACEHOLDERS_DIR = ASSETS_DIR / "placeholders"

STORAGE_DIR = PROJECT_ROOT / "storage"
DATABASE_DIR = STORAGE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "smart_mirror.db"
UPLOADS_DIR = STORAGE_DIR / "uploads"
BACKUPS_DIR = STORAGE_DIR / "backups"
EXPORTS_DIR = STORAGE_DIR / "exports"

LOGS_DIR = PROJECT_ROOT / "logs"


def ensure_directories() -> None:
    directories = [
        DATA_DIR,
        IMAGE_DIR,
        SHIRT_IMAGE_DIR,
        PANTS_IMAGE_DIR,
        ASSETS_DIR,
        ICONS_DIR,
        MAPS_DIR,
        PLACEHOLDERS_DIR,
        STORAGE_DIR,
        DATABASE_DIR,
        UPLOADS_DIR,
        BACKUPS_DIR,
        EXPORTS_DIR,
        LOGS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def resolve_project_path(relative_path: str | None) -> Path | None:
    if not relative_path:
        return None

    path = Path(relative_path)

    if path.is_absolute():
        return path

    return PROJECT_ROOT / path