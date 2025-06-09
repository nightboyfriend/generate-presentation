from fastapi.testclient import TestClient
from generate_presentation.main import app
import os
import json

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Добро пожаловать в API генерации презентаций!"}

def test_generate_from_topic():
    # Пример данных
    data = {
        "topic": "Космос",
        "slide_count": 3,  # Учитываем титульный слайд
        "output_path": "test_output.pptx"
    }
    response = client.post("/generate-from-topic/", data={"request": json.dumps(data)})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert os.path.exists("test_output.pptx")
    # Очистка
    if os.path.exists("test_output.pptx"):
        os.remove("test_output.pptx")