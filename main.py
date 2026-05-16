import os
import uuid
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from agent import run_eda_agent
from report import generate_report

app = FastAPI(title="EDA Agent")

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/static",  StaticFiles(directory="static"),  name="static")


@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "running"}


@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):

    # Step 1: validate
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # Step 2: save upload
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    upload_path = os.path.join("uploads", unique_name)

    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Step 3: read CSV
    try:
        df = pd.read_csv(upload_path)
    except Exception as e:
        os.remove(upload_path)          # clean up before raising
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {str(e)}")

    # Step 4: clean up upload file (we have df in memory now)
    os.remove(upload_path)

    # Step 5: sample large datasets so Groq never hits token limits
    # keep original for report generation, send sample to agent
    df_original = df.copy()
    if len(df) > 500:
        df_sample = df.sample(n=500, random_state=42)
        print(f"[Main] Large dataset detected ({len(df)} rows). Sampling 500 rows for agent.")
    else:
        df_sample = df

    # Step 6: run agent + generate report — both inside try/except
    # so ALL errors return JSON, never plain text
    try:
        result = run_eda_agent(df_sample)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    try:
        generate_report(df_original, result["summary"], result["charts"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report error: {str(e)}")

    # Step 7: build response
    chart_urls = [
        "/" + path.replace("\\", "/")
        for path in result["charts"]
    ]

    return JSONResponse({
        "summary":    result["summary"],
        "charts":     chart_urls,
        "rows":       int(df_original.shape[0]),
        "columns":    int(df_original.shape[1]),
        "report_url": "/outputs/report.pdf",
        "overview":   result.get("overview", {}),
        "statistics": result.get("statistics", {}),
        "outliers":   result.get("outliers", {})
    })