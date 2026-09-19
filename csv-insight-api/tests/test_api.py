from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_csv_analysis():
    csv = b"name,age,score\nAlice,22,91\nBob,25,85\nAlice,22,91\nDana,,88\n"
    response = client.post(
        "/analyze",
        files={"file": ("people.csv", BytesIO(csv), "text/csv")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["rows"] == 4
    assert data["columns"] == 3
    assert data["missing_values"]["age"] == 1
    assert data["duplicate_rows"] == 1
    assert data["numeric_summary"]["score"]["max"] == 91


def test_reject_non_csv():
    response = client.post(
        "/analyze",
        files={"file": ("notes.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400
