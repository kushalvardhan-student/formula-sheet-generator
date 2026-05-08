from __future__ import annotations

import io
import mimetypes
from pathlib import Path
from typing import Any

import easyocr
import fitz
import numpy as np
from docx import Document
from PIL import Image
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx", ".png", ".jpg", ".jpeg"}


class TextExtractor:
    def __init__(self) -> None:
        self._reader: easyocr.Reader | None = None

    @property
    def reader(self) -> easyocr.Reader:
        if self._reader is None:
            self._reader = easyocr.Reader(["en"], gpu=False)
        return self._reader

    def extract(self, file_name: str, file_bytes: bytes) -> dict[str, Any]:
        extension = Path(file_name).suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        if extension == ".txt":
            text = file_bytes.decode("utf-8", errors="ignore")
            return self._result(file_name, "text", text, False)

        if extension == ".docx":
            text = self._extract_docx(file_bytes)
            return self._result(file_name, "docx", text, False)

        if extension == ".pdf":
            pdf_result = self._extract_pdf(file_name, file_bytes)
            return pdf_result

        if extension in {".png", ".jpg", ".jpeg"}:
            text = self._ocr_image(file_bytes)
            return self._result(file_name, "image", text, True)

        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        raise ValueError(f"Unhandled file type: {mime_type}")

    def _result(self, file_name: str, source_type: str, text: str, used_ocr: bool) -> dict[str, Any]:
        clean_text = self._clean_text(text)
        return {
            "file_name": file_name,
            "source_type": source_type,
            "used_ocr": used_ocr,
            "text": clean_text,
            "characters": len(clean_text),
        }

    def _extract_docx(self, file_bytes: bytes) -> str:
        document = Document(io.BytesIO(file_bytes))
        lines = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(lines)

    def _extract_pdf(self, file_name: str, file_bytes: bytes) -> dict[str, Any]:
        direct_text = self._extract_text_pdf(file_bytes)
        if len(direct_text.strip()) >= 80:
            return self._result(file_name, "pdf-text", direct_text, False)

        ocr_text = self._ocr_pdf(file_bytes)
        return self._result(file_name, "pdf-image", ocr_text, True)

    def _extract_text_pdf(self, file_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    def _ocr_pdf(self, file_bytes: bytes) -> str:
        document = fitz.open(stream=file_bytes, filetype="pdf")
        page_texts: list[str] = []
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            page_texts.append(self._ocr_image(buffer.getvalue()))
        return "\n".join(page_texts)

    def _ocr_image(self, file_bytes: bytes) -> str:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        results = self.reader.readtext(np.array(image), detail=0, paragraph=True)
        return "\n".join(results)

    def _clean_text(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        filtered = [line for line in lines if line]
        return "\n".join(filtered)
