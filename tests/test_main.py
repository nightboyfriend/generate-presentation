from fastapi.testclient import TestClient
from generate_presentation.main import app
import os
import json

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Добро пожаловать в API генерации презентаций!"}

def test_generate_from_topic_normal():
    # Пример данных для обычного режима
    data = {
        "topic": "Космос",
        "slide_count": 3,
        "output_path": "test_output_normal.pptx",
        "template_mode": False
    }
    response = client.post("/generate-from-topic/", data={"request": json.dumps(data)})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert os.path.exists("test_output_normal.pptx")
    # Очистка
    if os.path.exists("test_output_normal.pptx"):
        os.remove("test_output_normal.pptx")

def test_generate_from_topic_template():
    # Пример данных для шаблонного режима
    data = {
        "topic": "Космос",
        "slide_count": 4,  # Титульный + 2 основных + последний
        "output_path": "test_output_template.pptx",
        "template_mode": True
    }
    response = client.post("/generate-from-topic/", data={"request": json.dumps(data)})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert os.path.exists("test_output_template.pptx")
    # Очистка
    if os.path.exists("test_output_template.pptx"):
        os.remove("test_output_template.pptx")

def test_generate_from_topic_template_invalid_slide_count():
    # Проверка валидации slide_count в шаблонном режиме
    data = {
        "topic": "Космос",
        "slide_count": 2,  # Меньше минимального
        "output_path": "test_output_invalid.pptx",
        "template_mode": True
    }
    response = client.post("/generate-from-topic/", data={"request": json.dumps(data)})
    assert response.status_code == 422
    assert "Количество слайдов для шаблонного режима должно быть от 3 до 20" in response.json()["detail"]