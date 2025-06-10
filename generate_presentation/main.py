from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from generate_presentation.models import PresentationRequest, GenerateRequest
from generate_presentation.presentation_generator import generate_presentation
from generate_presentation.llm import LLM
import os
import shutil
from pathlib import Path
from typing import List
from loguru import logger
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()
IMAGE_API_URL = f"{os.environ.get('IMAGE_API_HOST', 'http://192.168.0.59')}:{os.environ.get('IMAGE_API_PORT', '8087')}/llm_tools/image_generate"

app = FastAPI(title="Generate Presentation API")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="generate_presentation/static"), name="static")

llm = LLM()

async def generate_image(description: str, slide_index: int) -> str:
    async with aiohttp.ClientSession() as session:
        params = {
            "text": description,
            "width": 768,
            "height": 768,
            "return_format": "url"
        }
        try:
            async with session.post(IMAGE_API_URL, params=params) as response:
                if response.status != 200:
                    logger.error(f"Ошибка API изображений: {await response.text()}")
                    return None
                image_url = await response.text()
                image_url = image_url.strip('"')
                async with session.get(image_url) as img_response:
                    if img_response.status != 200:
                        logger.error(f"Ошибка загрузки изображения: {img_response.status}")
                        return None
                    file_path = UPLOAD_DIR / f"slide_{slide_index}.png"
                    with file_path.open("wb") as f:
                        f.write(await img_response.read())
                    return str(file_path)
        except Exception as e:
            logger.error(f"Ошибка генерации изображения: {e}")
            return None

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API генерации презентаций!"}

@app.post("/generate-from-topic/")
async def generate_from_topic(
    request: str = Form(...)
):
    try:
        request_data = json.loads(request)
        gen_request = GenerateRequest(**request_data)
    except json.JSONDecodeError:
        logger.error("Неверный формат JSON в поле 'request'")
        raise HTTPException(status_code=422, detail="Неверный формат JSON в поле 'request'")
    except Exception as e:
        logger.error(f"Ошибка валидации данных: {e}")
        raise HTTPException(status_code=422, detail=f"Ошибка валидации данных: {str(e)}")

    if gen_request.template_mode and (gen_request.slide_count < 3 or gen_request.slide_count > 20):
        raise HTTPException(status_code=422, detail="Количество слайдов для шаблонного режима должно быть от 3 до 20")

    slide_count_for_llm = gen_request.slide_count - 1 if not gen_request.template_mode else gen_request.slide_count - 2
    prompt = f"Сгенерируй данные для презентации на тему '{gen_request.topic}'. Верни результат в формате JSON, содержащем список слайдов, каждый из которых имеет поля 'zagolovok' (заголовок слайда) и 'opisanie' (описание слайда 200-230 слов). Количество слайдов: {slide_count_for_llm}. Пример: [{{\"zagolovok\": \"Слайд 1\", \"opisanie\": \"Описание слайда 1\"}}, {{\"zagolovok\": \"Слайд 2\", \"opisanie\": \"Описание слайда 2\"}}]"
    system_prompt = "The output is in JSON format. Return a list of objects with 'zagolovok' and 'opisanie' fields."

    try:
        slide_data = llm.llama_json(prompt, system_prompt=system_prompt)
        logger.debug(f"Данные от LLM: {slide_data}")
        if isinstance(slide_data, dict) and 'slides' in slide_data:
            slide_data = slide_data['slides']
        if not isinstance(slide_data, list):
            logger.error("LLM вернул некорректный формат данных, ожидался список")
            raise ValueError(f"LLM вернул некорректный формат данных: {slide_data}")
        for slide in slide_data:
            if not all(key in slide for key in ["zagolovok", "opisanie"]):
                logger.error(f"Некорректная структура слайда: {slide}")
                raise ValueError(f"Слайд не содержит необходимые поля: {slide}")
    except Exception as e:
        logger.error(f"Ошибка при запросе к LLM: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации данных слайдов: {str(e)}")
    for i, slide in enumerate(slide_data):
        image_path = await generate_image(slide["opisanie"], i)
        if image_path:
            slide["photo"] = image_path
        else:
            logger.warning(f"Не удалось сгенерировать изображение для слайда {i+1}")

    output_path = gen_request.output_path if gen_request.output_path.endswith('.pptx') else "output.pptx"
    generate_presentation(slide_data, gen_request.slide_count, output_path, gen_request.topic, gen_request.template_mode)
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=500, detail="Не удалось сгенерировать презентацию")
    
    return FileResponse(
        path=output_path,
        filename=output_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

@app.on_event("shutdown")
async def cleanup():
    if UPLOAD_DIR.exists():
        for file in UPLOAD_DIR.glob("*"):
            file.unlink()
        try:
            UPLOAD_DIR.rmdir()
        except:
            pass
    if os.path.exists("output.pptx"):
        os.remove("output.pptx")