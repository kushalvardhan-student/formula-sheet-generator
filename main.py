from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from formula_extractor import FormulaExtractor
from ocr import TextExtractor
from ollama_client import OllamaClient
from pdf_generator import build_formula_pdf, build_formula_txt


app = FastAPI(title="FormulaForge AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ocr_service = TextExtractor()
ollama_client = OllamaClient()
formula_extractor = FormulaExtractor(ollama_client)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/process-notes")
async def process_notes(files: list[UploadFile] = File(...)) -> dict[str, Any]:
    extracted_files = []
    full_text_parts: list[str] = []

    for upload in files:
        file_bytes = await upload.read()
        if not file_bytes:
            continue

        try:
            extracted = ocr_service.extract(upload.filename or "unknown", file_bytes)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process {upload.filename}: {error}",
            ) from error

        extracted_files.append(extracted)
        full_text_parts.append(f"File: {extracted['file_name']}\n{extracted['text']}")

    combined_text = "\n\n".join(part for part in full_text_parts if part.strip())
    if not combined_text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in uploaded files.")

    try:
        structured = formula_extractor.extract_formulas(combined_text)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"AI extraction failed: {error}") from error

    return {
        "extracted_files": extracted_files,
        "combined_text": combined_text,
        "formula_sheet": structured,
    }


@app.post("/api/chat")
async def chat_with_notes(
    question: str = Form(...),
    combined_text: str = Form(...),
    formula_sheet: str = Form(...),
) -> dict[str, str]:
    try:
        parsed_sheet = json.loads(formula_sheet)
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=400, detail="Invalid formula sheet payload.") from error

    try:
        answer = formula_extractor.answer_question(question, combined_text, parsed_sheet)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Chat generation failed: {error}") from error

    return {"answer": answer}


@app.post("/api/download/pdf")
async def download_pdf(payload: dict[str, Any]) -> Response:
    pdf_bytes = build_formula_pdf(payload)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=formulaforge-ai.pdf"},
    )


@app.post("/api/download/txt")
async def download_txt(payload: dict[str, Any]) -> Response:
    text_content = build_formula_txt(payload)
    return Response(
        content=text_content.encode("utf-8"),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=formulaforge-ai.txt"},
    )
