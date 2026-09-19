# CSV Insight API

A lightweight FastAPI service that automatically profiles CSV datasets.

Upload a CSV file and the API returns its shape, data types, missing values,
duplicate rows, numeric statistics, a data-quality score, and a five-row preview.

## Why this project?

Small data pipelines often need a quick validation step before data is loaded
into a database or analytics system. CSV Insight API provides that first-pass
check through a simple REST endpoint.

## Features

- CSV upload through REST API
- Column and row counts
- Automatic data-type detection
- Missing-value analysis
- Duplicate-row detection
- Min, max, mean and median for numeric columns
- Simple 0-100 data-quality score
- Data preview
- File-size validation
- Swagger/OpenAPI documentation
- Docker support
- Automated tests

## Run locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Use the `/analyze` endpoint and upload `sample.csv`.

## Example response

```json
{
  "filename": "sample.csv",
  "rows": 6,
  "columns": 4,
  "duplicate_rows": 0,
  "quality_score": 97.5
}
```

The actual response also contains column types, missing-value counts,
numeric statistics and a data preview.

## Tests

```bash
pytest
```

## Docker

```bash
docker build -t csv-insight-api .
docker run -p 8000:8000 csv-insight-api
```

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/analyze` | Analyze an uploaded CSV |

## Tech stack

Python, FastAPI, Pandas, Pytest, Docker.
