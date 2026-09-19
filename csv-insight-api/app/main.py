from io import BytesIO

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(
    title="CSV Insight API",
    version="1.0.0",
    description="Upload a CSV file and receive an automatic data-quality and statistical summary.",
)

MAX_FILE_SIZE = 5 * 1024 * 1024


def _safe_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


@app.get("/")
def root():
    return {"name": "CSV Insight API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is larger than 5 MB.")

    try:
        df = pd.read_csv(BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    if df.empty and len(df.columns) == 0:
        raise HTTPException(status_code=400, detail="CSV has no columns.")

    numeric = df.select_dtypes(include="number")
    numeric_summary = {}

    for column in numeric.columns:
        series = numeric[column]
        numeric_summary[column] = {
            "min": _safe_value(series.min()),
            "max": _safe_value(series.max()),
            "mean": _safe_value(series.mean()),
            "median": _safe_value(series.median()),
        }

    missing = {column: int(value) for column, value in df.isna().sum().items()}
    missing_percent = {
        column: round((count / len(df) * 100), 2) if len(df) else 0.0
        for column, count in missing.items()
    }

    quality_score = 100.0
    if df.size:
        quality_score -= (sum(missing.values()) / df.size) * 60
    if len(df):
        quality_score -= (int(df.duplicated().sum()) / len(df)) * 40

    return {
        "filename": file.filename,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "column_types": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "missing_values": missing,
        "missing_percent": missing_percent,
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_summary": numeric_summary,
        "quality_score": round(max(0.0, quality_score), 2),
        "preview": df.head(5).where(pd.notna(df), None).to_dict(orient="records"),
    }
