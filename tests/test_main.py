from fastapi.testclient import TestClient
from generate_presentation.main import app
import os

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Добро пожаловать в API генерации презентаций!"}

def test_generate_presentation():
    # Пример данных
    data = {
        "slides": [
            {"zagolovok": "Слайд 1", "opisanie": "Описание 1", "photo": "image1.png"},
            {"zagolovok": "Слайд 2", "opisanie": "Описание 2", "photo": "image2.png"}
        ],
        "slide_count": 2,
        "output_path": "test_output.pptx"
    }
    # Имитация загрузки файлов
    files = [
        ("files", ("image1.png", b"fake image content", "image/png")),
        ("files", ("image2.png", b"fake image content", "image/png"))
    ]
    response = client.post("/generate-presentation/", json=data, files=files)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert os.path.exists("test_output.pptx")
    # Очистка
    if os.path.exists("test_output.pptx"):
        os.remove("test_output.pptx")