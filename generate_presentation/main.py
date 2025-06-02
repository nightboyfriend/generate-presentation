from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from generate_presentation.models import PresentationRequest
from generate_presentation.presentation_generator import generate_presentation
import os
import shutil
from pathlib import Path
from typing import List
import json

app = FastAPI(title="Generate Presentation API")

# Директория для временного хранения файлов
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Подключение статических файлов (для frontend)
app.mount("/static", StaticFiles(directory="generate_presentation/static"), name="static")

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API генерации презентаций!"}

@app.post("/generate-presentation/")
async def create_presentation(
    request: str = Form(...),  # Получаем поле 'request' как строку из FormData
    files: List[UploadFile] = File(default=[])
):
    try:
        # Распарсим строку JSON в словарь
        request_data = json.loads(request)
        # Валидируем данные через модель Pydantic
        presentation_request = PresentationRequest(**request_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Неверный формат JSON в поле 'request'")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Ошибка валидации данных: {str(e)}")

    # Подготовка данных слайдов
    slide_data = [slide.dict() for slide in presentation_request.slides]
    
    # Сохранение загруженных изображений
    for i, file in enumerate(files):
        if i < len(slide_data) and slide_data[i].get("photo"):
            file_path = UPLOAD_DIR / file.filename
            try:
                with file_path.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                # Обновляем путь к фото в данных слайда
                slide_data[i]["photo"] = str(file_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла {file.filename}: {e}")
    
    # Генерация презентации
    output_path = presentation_request.output_path if presentation_request.output_path.endswith('.pptx') else "output.pptx"
    generate_presentation(slide_data, presentation_request.slide_count, output_path)
    
    # Проверка существования файла
    if not os.path.exists(output_path):
        raise HTTPException(status_code=500, detail="Не удалось сгенерировать презентацию")
    
    # Возврат файла для скачивания
    return FileResponse(
        path=output_path,
        filename=output_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

@app.on_event("shutdown")
async def cleanup():
    # Удаление временных файлов при завершении работы
    if UPLOAD_DIR.exists():
        for file in UPLOAD_DIR.glob("*"):
            file.unlink()
        try:
            UPLOAD_DIR.rmdir()
        except:
            pass
    if os.path.exists("output.pptx"):
        os.remove("output.pptx")