from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    product_code: str
    name: str
    department: str
    category: str
    price: float

    colour: str = ""
    description: str = ""
    image_path: str = ""
    available: bool = True
    discount: bool = False
    discount_price: Optional[float] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    location: str = ""
    tryon_enabled: bool = False
    tryon_category: Optional[str] = None
    active: bool = True

    sizes: list[dict] = field(default_factory=list)

    width_scale: float = 1.0
    height_scale: float = 1.0
    vertical_offset: float = 0.0
    horizontal_offset: int = 0

    id: Optional[int] = None
