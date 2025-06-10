from pydantic import BaseModel
from typing import List, Optional

class SlideData(BaseModel):
    zagolovok: str
    opisanie: str
    photo: Optional[str] = None

class PresentationRequest(BaseModel):
    slides: List[SlideData]
    slide_count: int
    output_path: str = "output.pptx"

class GenerateRequest(BaseModel):
    topic: str
    slide_count: int
    output_path: str = "output.pptx"
    template_mode: bool = False