from pydantic import BaseModel
from typing import List, Optional

class SlideData(BaseModel):
    zagolovok: str
    opisanie: str
    photo: Optional[str] = None  # Путь к фото, будет обновлен после загрузки

class PresentationRequest(BaseModel):
    slides: List[SlideData]
    slide_count: int
    output_path: str = "output.pptx"