## PDF→Markdown Tool — Copilot Instructions

This repository is a small web app that converts regions of PDFs into Markdown (text + embedded images).
Keep instructions concise and only make changes that follow the project's existing patterns.

Key facts for working in this codebase
- Backend: FastAPI app at `backend/main.py`. Routes:
  - `POST /upload_pdf` — saves uploaded files to `backend/uploads` and returns `http://localhost:8000/pdf/{filename}`
  - `POST /extract_text` — extracts text from a given region using `utils/pdf_utils.py`
  - `POST /extract_content` — extracts text and images (returns base64 images embedded into markdown)
- PDF processing: `backend/utils/pdf_utils.py` uses PyMuPDF (`fitz`) to read pages, clip to a rectangle, extract text and images. Image extraction filters images by intersection with the selection rectangle.
- Frontend: React + Vite. Main app in `frontend/src/App.jsx`. PDF viewer with selection is `frontend/src/components/PDFViewer.jsx`. API calls are in `frontend/src/services/api.js` and target `http://localhost:8000`.
- Dev scripts:
  - Backend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
  - Frontend: `cd frontend && npm install && npm run dev`
  - Docker: Dockerfile builds the backend (includes extra system deps for PyMuPDF). The container starts `uvicorn main:app --host 0.0.0.0 --port 8000`.

Project-specific conventions and patterns
- Uploads directory: backend writes uploaded PDFs to `uploads` (relative to `backend/`). Do not change this path without updating frontend upload responses and Docker start/volume config.
- Page indexing: the backend expects 0-indexed page numbers (see `PDFViewer` where `onSelect` sends `page: pageNumber - 1`). Preserve that contract when editing endpoints or client code.
- Selection coords: `PDFViewer` sends pixel coordinates x1,y1,x2,y2 directly; backend `pdf_utils` consumes them as PyMuPDF coordinates. When changing viewer scale/width, ensure coordinates remain aligned (look at `Page width={600}` and Stage width=600 in `PDFViewer.jsx`).
- Images: `extract_content_from_region` returns images as base64 strings with the file extension in `ext`. The backend constructs Markdown using data URIs in `main.py`. If adding file-based image exports, update both the returned JSON and frontend handling.

Integration and external dependencies
- Python: required packages in `backend/requirements.txt` — fastapi, uvicorn, pymupdf, python-multipart.
- Frontend: `frontend/package.json` — axios, react-pdf, react-konva, pdfjs-dist. Vite is used for dev server.
- Docker: The Dockerfile installs system libs required by PyMuPDF (`libmupdf-dev`, `libmupdf-tools`). If CI runners or deployment targets are different (e.g., Alpine), ensure equivalent system packages are available.

Developer workflows (explicit commands)
- Start backend (dev):
  - Open a terminal in the `backend` folder and run:
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload
- Start frontend (dev):
  - Open a terminal in the `frontend` folder and run:
    cd frontend
    npm install
    npm run dev
- Build Docker image (backend-only):
  - From repo root:
    docker build -t pdf2md-backend .
  - Note: Dockerfile only builds and runs the backend. The frontend is expected to run separately in development.

What to avoid / common pitfalls
- Do not change the upload URL format returned by `POST /upload_pdf` (it is used directly by the frontend to load PDFs).
- Avoid changing coordinate conventions (0-index vs 1-index pages) — this will break selection mapping.
- When modifying image extraction, preserve the `ext` field and base64 `data` format unless you update both backend and frontend consumers.

Examples to reference when coding
- Add a new backend route: follow patterns in `backend/main.py` (use `Form(...)` for fields and return JSON with simple keys). Keep CORS middleware settings if you add new endpoints.
- Modify extraction logic: `backend/utils/pdf_utils.py` shows how text is clipped with `fitz.Rect` and images filtered by `page.get_image_bbox(img)`. Keep try/except blocks used there to avoid breaking on malformed PDFs.

When writing tests or changes
- There are no tests in the repo. If you add tests, use pytest and place them under `backend/tests` or `frontend/__tests__`. For backend tests, run them in an environment with PyMuPDF available; Dockerfile shows system deps needed.

If you need clarification, ask the repo owner for expected hosting (Railway/Render) and whether uploads should persist across deploys — current README suggests Railway with persistent storage.

---
If this file misses anything you'd like the agent to know (deploy vars, CI, or preferred code style), tell me and I'll update it.
