from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from utils.pdf_utils import extract_text_from_region, extract_content_from_region

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile):
    pdf_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    return {"pdf_url": f"http://localhost:8000/pdf/{file.filename}"}

@app.get("/pdf/{filename}")
async def get_pdf(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    return FileResponse(path, media_type="application/pdf")

@app.post("/extract_text")
async def extract_text_api(
    filename: str = Form(...),
    page_number: int = Form(...),
    x1: float = Form(...),
    y1: float = Form(...),
    x2: float = Form(...),
    y2: float = Form(...),
):
    path = os.path.join(UPLOAD_DIR, filename)
    text = extract_text_from_region(path, page_number, x1, y1, x2, y2)
    md_path = os.path.join(UPLOAD_DIR, "output.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text)
    return {"text": text, "markdown_path": md_path}

@app.post("/extract_content")
async def extract_content_api(
    filename: str = Form(...),
    page_number: int = Form(...),
    x1: float = Form(...),
    y1: float = Form(...),
    x2: float = Form(...),
    y2: float = Form(...),
):
    """Extract both text and images from a region."""
    try:
        path = os.path.join(UPLOAD_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(path):
            return {"error": f"File {filename} not found"}
        
        content = extract_content_from_region(path, page_number, x1, y1, x2, y2)
        
        # Build markdown with embedded images
        markdown = content["text"]
        
        if content["has_images"]:
            if markdown:
                markdown += "\n\n"
            
            for idx, img in enumerate(content["images"]):
                markdown += f"![Image {idx + 1}](data:image/{img['ext']};base64,{img['data']})\n\n"
        
        return {
            "text": content["text"],
            "markdown": markdown,
            "has_images": content["has_images"],
            "image_count": len(content["images"])
        }
        
    except Exception as e:
        print(f"Error in extract_content_api: {e}")
        return {"error": f"Failed to extract content: {str(e)}"}
