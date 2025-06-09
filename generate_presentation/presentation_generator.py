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

def add_title_slide(prs: Presentation, topic: str) -> None:
    """Добавляет титульный слайд с темой презентации, отцентрированным по центру."""
    slide_layout = prs.slide_layouts[0]  # Используем пустой или титульный шаблон
    slide = prs.slides.add_slide(slide_layout)

    # Добавляем текстовое поле для темы
    title = slide.shapes.title
    if title:
        title.text = topic
        title.text_frame.paragraphs[0].font.name = 'Arial'
        title.text_frame.paragraphs[0].font.size = Pt(36)  # Увеличиваем размер шрифта
        title.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        title.text_frame.paragraphs[0].font.bold = True
        # Центрируем текстовое поле
        title.left = Inches(0)
        title.top = Inches(2)  # Примерно середина слайда по вертикали
        title.width = Inches(10)
        title.height = Inches(1.5)

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

def generate_presentation(data: List[Dict], slide_count: int, output_path: str, topic: str) -> None:
    if not data and not topic:
        print("Нет данных или темы для генерации презентации")
        return
    prs = create_presentation(slide_count)
    # Добавляем титульный слайд с темой
    if topic:
        add_title_slide(prs, topic)
    # Добавляем остальные слайды
    for i, slide_data in enumerate(data[:slide_count]):
        add_slide(prs, slide_data)
    try:
        prs.save(output_path)
        print(f"Презентация сохранена в {output_path}")
    except Exception as e:
        print(f"Ошибка сохранения презентации: {e}")