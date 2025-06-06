from fastapi.testclient import TestClient
from generate_presentation.main import app
import os

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Добро пожаловать в API генерации презентаций!"}

def test_generate_from_topic():
    # пример
    data = {
        "topic": "Космос",
        "slide_count": 2,
        "output_path": "test_output.pptx"
    }
    response = client.post("/generate-from-topic/", data={"request": json.dumps(data)})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert os.path.exists("test_output.pptx")

    if os.path.exists("test_output.pptx"):
        os.remove("test_output.pptx")