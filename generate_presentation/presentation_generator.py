from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
import os
from typing import List, Dict

def create_presentation(slide_count: int) -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)
    return prs

def add_slide(prs: Presentation, data: Dict) -> None:
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)

    if 'zagolovok' in data and data['zagolovok']:
        title = slide.shapes.title
        if title:
            title.text = data['zagolovok']
            title.text_frame.paragraphs[0].font.name = 'Arial'
            title.text_frame.paragraphs[0].font.size = Pt(28)
            title.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            title.top = Inches(0.5)
            title.width = Inches(10)
            content.height = Inches(0.25)
            title.text_frame.paragraphs[0].font.bold = True

    if 'opisanie' in data and data['opisanie']:
        if len(slide.placeholders) > 1:
            content = slide.placeholders[1]
            content.text_frame.clear()
            p = content.text_frame.add_paragraph()
            p.text = data['opisanie']
            p.font.name = 'Arial'
            p.font.size = Pt(14)
            p.alignment = PP_ALIGN.LEFT
            content.left = Inches(0.5)
            content.top = Inches(1)
            content.width = Inches(5)
            content.height = Inches(4.5)

    if 'photo' in data and data['photo'] and os.path.exists(data['photo']):
        try:
            slide.shapes.add_picture(data['photo'], Inches(6), Inches(1), width=Inches(3))
        except Exception as e:
            print(f"Ошибка добавления фото для слайда '{data.get('zagolovok', 'Неизвестно')}': {e}")

def generate_presentation(data: List[Dict], slide_count: int, output_path: str) -> None:
    if not data:
        print("Нет данных для генерации презентации")
        return
    prs = create_presentation(slide_count)
    for i, slide_data in enumerate(data[:slide_count]):
        add_slide(prs, slide_data)
    try:
        prs.save(output_path)
        print(f"Презентация сохранена в {output_path}")
    except Exception as e:
        print(f"Ошибка сохранения презентации: {e}")