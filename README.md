# PDF to Markdown Tool

A web application that converts PDF content to Markdown format with text and image extraction capabilities, and lets you share the extracted content as a public web link.

## Features

- Upload PDF files
- Navigate through PDF pages
- Select regions to extract text and images
- Export extracted content as Markdown
- Real-time preview of extracted content
- Generate shareable web links that render your Markdown as a nicely formatted page

## Tech Stack

- **Frontend**: React + Vite + Konva + React-PDF
- **Backend**: FastAPI + PyMuPDF + Uvicorn + markdown2
- **File Processing**: PDF text and image extraction

## How It Works

- **Extraction flow**
  - Upload a PDF from the frontend; the file is stored by the FastAPI backend under `uploads/`.
  - Use the PDF viewer to navigate pages and drag-select regions.
  - The frontend calls `POST /extract_content`, which:
    - Extracts text from the selected region.
    - Extracts images that intersect the region and embeds them into the markdown as `![Image](data:image/...)`.
  - The selected regions are appended into a single **Extracted Markdown Content** area in the UI where you can edit the markdown.

- **Sharing flow**
  - Click **“🔗 Get shareable link”** in the UI.
  - The frontend sends the current markdown (and an optional title derived from the PDF filename) to `POST /save_markdown`.
  - The backend:
    - Stores the markdown under `uploads/pages/<slug>.md`.
    - Returns a public URL like `BASE_URL/share/<slug>`.
  - Visiting that URL calls `GET /share/{slug}`, which:
    - Loads the stored markdown.
    - Converts it to HTML using `markdown2` with GitHub-like styling (headings, lists, code blocks, tables, images, etc.).

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python backend
3. Deploy with persistent file storage

### Render
1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Environment Variables
- `PORT`: Automatically set by hosting platform
- `UPLOAD_DIR`: Set to `/tmp/uploads` for serverless platforms

## API Endpoints

- `POST /upload_pdf` - Upload a PDF file
- `GET /pdf/{filename}` - Serve PDF file
- `POST /extract_text` - Extract text from region
- `POST /extract_content` - Extract text and images from region

## File Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── utils/
│       └── pdf_utils.py     # PDF processing utilities
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── components/
│   │   │   └── PDFViewer.jsx # PDF viewer component
│   │   └── services/
│   │       └── api.js       # API service functions
│   └── package.json         # Node.js dependencies
└── uploads/                 # PDF storage directory
```

