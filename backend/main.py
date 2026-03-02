from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
import os
import uuid
import markdown2
from utils.pdf_utils import extract_text_from_region, extract_content_from_region

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

PAGES_DIR = os.path.join(UPLOAD_DIR, "pages")
os.makedirs(PAGES_DIR, exist_ok=True)

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile):
    pdf_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    return {"pdf_url": f"{BASE_URL}/pdf/{file.filename}"}

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


@app.post("/save_markdown")
async def save_markdown(
    content: str = Form(...),
    title: str = Form(None),
):
    """
    Save extracted Markdown as a shareable web page and return its URL.
    """
    if not content.strip():
        return {"error": "Content is empty"}

    slug = uuid.uuid4().hex[:8]
    filename = f"{slug}.md"
    path = os.path.join(PAGES_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        if title:
            f.write(f"# {title}\n\n")
        f.write(content)

    return {
        "slug": slug,
        "url": f"{BASE_URL}/share/{slug}",
    }


@app.get("/share/{slug}", response_class=HTMLResponse)
async def get_shared_page(slug: str):
    """
    Serve a simple HTML page that renders the stored Markdown.
    """
    filename = f"{slug}.md"
    path = os.path.join(PAGES_DIR, filename)

    if not os.path.exists(path):
        return HTMLResponse("<h1>Not found</h1>", status_code=404)

    with open(path, "r", encoding="utf-8") as f:
        markdown = f.read()

    # Use the first Markdown heading as the title if present
    title = "Shared Markdown"
    for line in markdown.splitlines():
        if line.startswith("# "):
            title = line[2:].strip() or title
            break

    # Convert markdown to HTML with some extras for a GitHub-like feel
    html_body = markdown2.markdown(
        markdown,
        extras=[
            "fenced-code-blocks",
            "tables",
            "strike",
            "task_list",
            "cuddled-lists",
        ],
    )

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
            body {{
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                max-width: 860px;
                margin: 2rem auto;
                padding: 0 1rem 3rem;
                line-height: 1.6;
                background: #f6f8fa;
                color: #24292e;
            }}
            .markdown-body {{
                background: #ffffff;
                border-radius: 6px;
                border: 1px solid #d0d7de;
                padding: 24px 32px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            }}
            .markdown-body h1,
            .markdown-body h2,
            .markdown-body h3,
            .markdown-body h4,
            .markdown-body h5,
            .markdown-body h6 {{
                font-weight: 600;
                margin-top: 1.5em;
                margin-bottom: 0.75em;
            }}
            .markdown-body h1 {{
                font-size: 2rem;
                border-bottom: 1px solid #d0d7de;
                padding-bottom: 0.3em;
            }}
            .markdown-body h2 {{
                font-size: 1.6rem;
                border-bottom: 1px solid #d0d7de;
                padding-bottom: 0.3em;
            }}
            .markdown-body p {{
                margin: 0.5em 0 1em;
            }}
            .markdown-body code {{
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
                font-size: 0.9em;
                background: rgba(175,184,193,0.2);
                border-radius: 4px;
                padding: 0.1em 0.3em;
            }}
            .markdown-body pre code {{
                background: none;
                padding: 0;
            }}
            .markdown-body pre {{
                background: #0d1117;
                color: #c9d1d9;
                padding: 12px 16px;
                border-radius: 6px;
                overflow: auto;
                font-size: 0.9em;
            }}
            .markdown-body a {{
                color: #0969da;
                text-decoration: none;
            }}
            .markdown-body a:hover {{
                text-decoration: underline;
            }}
            .markdown-body img {{
                max-width: 100%;
                border-radius: 4px;
                margin: 0.75em 0;
            }}
            .markdown-body ul,
            .markdown-body ol {{
                padding-left: 1.5em;
                margin: 0.5em 0 1em;
            }}
            .markdown-body blockquote {{
                border-left: 0.25em solid #d0d7de;
                color: #57606a;
                padding: 0 1em;
                margin: 0.5em 0 1em;
            }}
            .markdown-body table {{
                border-collapse: collapse;
                margin: 1em 0;
                width: 100%;
            }}
            .markdown-body table th,
            .markdown-body table td {{
                border: 1px solid #d0d7de;
                padding: 6px 13px;
            }}
            .markdown-body table tr:nth-child(2n) {{
                background-color: #f6f8fa;
            }}
        </style>
    </head>
    <body>
        <article class="markdown-body">
            {html_body}
        </article>
    </body>
    </html>
    """

    return HTMLResponse(html)
