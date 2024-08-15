import requests

BASE_URL = "http://127.0.0.1:8000"

def test_get_syllabus_valid_input():
    response = requests.post(f"{BASE_URL}/get_syllabus", json={"grade": "10", "subject": "Math"})
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_syllabus_with_pdf():
    response = requests.post(f"{BASE_URL}/get_syllabus", params={"Type": "pdf"}, json={"grade": "10", "subject": "Math"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_get_syllabus_with_word():
    response = requests.post(f"{BASE_URL}/get_syllabus", params={"Type": "word"}, json={"grade": "10", "subject": "Math"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

def test_get_syllabus_missing_required_field():
    response = requests.post(f"{BASE_URL}/get_syllabus", json={"subject": "Math"})
    assert response.status_code == 422  # Unprocessable Entity

def test_get_syllabus_invalid_type():
    response = requests.post(f"{BASE_URL}/get_syllabus", params={"Type": "unsupported_type"}, json={"grade": "10", "subject": "Math"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"

def test_get_syllabus_empty_optional_fields():
    response = requests.post(f"{BASE_URL}/get_syllabus", json={"grade": "10", "subject": "Math", "Syllabus_type": "", "instructions": ""})
    assert response.status_code == 500
    assert response.data

def test_executor_exception():
    response = requests.post(f"{BASE_URL}/get_syllabus", json={"grade": "10", "subject": "Math"})
    assert response.status_code == 200
