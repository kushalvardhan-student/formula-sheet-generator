# FormulaForge AI

FormulaForge AI is a full-stack, hackathon-ready web app that converts study notes into a clean, topic-wise formula sheet using OCR and a local Ollama model.

## Features

- Drag-and-drop multi-file upload
- Support for PDF, TXT, DOCX, PNG, JPG, JPEG
- EasyOCR for handwritten note extraction
- Automatic detection of text-based vs image-based PDFs
- Ollama-powered formula extraction with structured JSON
- Topic-wise formula cards with short meanings, variables, and uses
- "Most Frequently Used Formulae" high-yield revision section
- Notes-only chatbot grounded in uploaded context
- Download generated output as PDF or TXT
- Responsive glassmorphism UI with dark/light mode and collapsible sections

## Project Structure

```text
FormulaForge AI/
├── backend/
│   ├── main.py
│   ├── ocr.py
│   ├── ollama_client.py
│   ├── formula_extractor.py
│   ├── pdf_generator.py
│   └── requirements.txt
├── frontend/
│   ├── components/
│   ├── src/
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Backend Setup

1. Create and activate a virtual environment:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Make sure Ollama is running locally:

```powershell
ollama serve
```

4. Pull the model you want to use:

```powershell
ollama pull gpt-oss:120b-cloud
```

If you want to switch back to the lighter model from the original spec:

```powershell
$env:OLLAMA_MODEL="qwen2.5:3b"
```

5. Run the FastAPI server:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup

1. Open a new terminal:

```powershell
cd frontend
```

2. Install dependencies:

```powershell
npm install
```

3. Start the development server:

```powershell
npm run dev
```

4. Optional API override:

Create a `.env` file inside `frontend/` if your backend is not running on `http://127.0.0.1:8000`.

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Flow

1. Frontend uploads multiple files to `/api/process-notes`
2. FastAPI extracts text directly where possible
3. OCR is used for handwritten images or image-only PDFs
4. Extracted text is sent to Ollama
5. Ollama returns structured JSON
6. Frontend renders formula cards and important formulas
7. Chat uses `/api/chat` with uploaded context only
8. Downloads are generated through `/api/download/pdf` and `/api/download/txt`

## Sample Prompts for the Chat Panel

- `Show integration formulas`
- `Explain Ohm's law`
- `Show formulas from thermodynamics`
- `List formulas from electrostatics`
- `Which formulas are used for probability?`

## Example Ollama Response Shape

```json
{
  "subject": "Physics",
  "topics": [
    {
      "topic_name": "Newtonian Mechanics",
      "formulas": [
        {
          "formula": "F = ma",
          "meaning": "Force equals mass into acceleration",
          "variables": [
            { "symbol": "F", "meaning": "Force" },
            { "symbol": "m", "meaning": "Mass" },
            { "symbol": "a", "meaning": "Acceleration" }
          ],
          "use": "Used in Newton's Second Law"
        }
      ]
    }
  ],
  "important_formulas": [
    {
      "formula": "F = ma",
      "meaning": "Core force relation",
      "use": "Used in mechanics problems"
    }
  ]
}
```

## Notes for Large Files

- The backend trims long prompts before sending them to Ollama to keep generation practical.
- Text PDFs are extracted directly first for speed.
- OCR is lazily initialized so the app starts faster.
- The UI shows upload and processing progress for a smoother demo.

## Recommended Demo Flow

1. Upload one typed PDF and one handwritten image.
2. Generate the formula sheet.
3. Expand topic sections.
4. Ask the chatbot for a formula category.
5. Download the result as PDF.
