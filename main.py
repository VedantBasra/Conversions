from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
import uuid
from typing import Optional
from utils import (
    convert_office_to_pdf, convert_images_to_pdf, convert_pdf_to_images,
    extract_images_from_pdf, convert_html_to_pdf, convert_markdown_to_pdf,
    convert_image_format
)


app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/docx", response_class=HTMLResponse)
async def docx_form(request: Request):
    return templates.TemplateResponse("docx.html", {"request": request})

@app.post("/docx")
async def handle_docx(request: Request, file: UploadFile = File(...)):
    return await handle_office_conversion(request, file, "docx.html")

@app.get("/pptx", response_class=HTMLResponse)
async def pptx_form(request: Request):
    return templates.TemplateResponse("pptx.html", {"request": request})

@app.post("/pptx")
async def handle_pptx(request: Request, file: UploadFile = File(...)):
    return await handle_office_conversion(request, file, "pptx.html")

@app.get("/xlsx", response_class=HTMLResponse)
async def xlsx_form(request: Request):
    return templates.TemplateResponse("xlsx.html", {"request": request})

@app.post("/xlsx")
async def handle_xlsx(request: Request, file: UploadFile = File(...)):
    return await handle_office_conversion(request, file, "xlsx.html")

async def handle_office_conversion(request: Request, file: UploadFile, template: str):
    task_id = str(uuid.uuid4())
    input_dir = os.path.join(UPLOAD_FOLDER, task_id)
    output_dir = os.path.join(PROCESSED_FOLDER, task_id)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    input_path = os.path.join(input_dir, file.filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())
    output_path = convert_office_to_pdf(input_path, output_dir)
    if output_path and os.path.exists(output_path):
        return templates.TemplateResponse(template, {
            "request": request,
            "task_id": task_id,
            "file_name": os.path.basename(output_path)
        })
    return templates.TemplateResponse(template, {
        "request": request,
        "error": "Conversion failed"
    })

@app.get("/images-to-pdf", response_class=HTMLResponse)
async def images_to_pdf_form(request: Request):
    return templates.TemplateResponse("images_to_pdf.html", {"request": request})

@app.post("/images-to-pdf")
async def images_to_pdf_upload(request: Request, files: list[UploadFile] = File(...)):
    task_id = str(uuid.uuid4())
    input_dir = os.path.join(UPLOAD_FOLDER, task_id)
    output_dir = os.path.join(PROCESSED_FOLDER, task_id)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    for file in files:
        path = os.path.join(input_dir, file.filename)
        with open(path, "wb") as f:
            f.write(await file.read())
        image_paths.append(path)
    output_path = os.path.join(output_dir, "images.pdf")
    result = convert_images_to_pdf(image_paths, output_path)
    if result:
        return templates.TemplateResponse("images_to_pdf.html", {
            "request": request,
            "task_id": task_id,
            "file_name": "images.pdf"
        })
    return templates.TemplateResponse("images_to_pdf.html", {
        "request": request,
        "error": "Conversion failed"
    })

@app.get("/pdf-to-images", response_class=HTMLResponse)
async def pdf_to_images_form(request: Request):
    return templates.TemplateResponse("pdf_to_images.html", {
        "request": request,
        "images": [],
        "zip_url": None
    })

@app.post("/pdf-to-images")
async def pdf_to_images_upload(request: Request, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    input_dir = os.path.join(UPLOAD_FOLDER, task_id)
    output_dir = os.path.join(PROCESSED_FOLDER, task_id)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    input_path = os.path.join(input_dir, file.filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())
    base_name = os.path.splitext(file.filename)[0]
    image_paths, zip_path = convert_pdf_to_images(input_path, output_dir, base_name)
    return templates.TemplateResponse("pdf_to_images.html", {
        "request": request,
        "task_id": task_id,
        "image_filenames": [os.path.basename(p) for p in image_paths],
        "zip_name": os.path.basename(zip_path)
    })

@app.get("/extract-images", response_class=HTMLResponse)
async def extract_images_form(request: Request):
    return templates.TemplateResponse("extract_images.html", {
        "request": request,
        "images": [],
        "zip_url": None
    })

@app.post("/extract-images")
async def extract_images_upload(request: Request, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    input_dir = os.path.join(UPLOAD_FOLDER, task_id)
    output_dir = os.path.join(PROCESSED_FOLDER, task_id)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    input_path = os.path.join(input_dir, file.filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())
    base_name = os.path.splitext(file.filename)[0]
    image_paths, zip_path = extract_images_from_pdf(input_path, output_dir, base_name)
    return templates.TemplateResponse("extract_images.html", {
        "request": request,
        "task_id": task_id,
        "image_filenames": [os.path.basename(p) for p in image_paths],
        "zip_name": os.path.basename(zip_path)
    })

@app.get("/markdown-to-pdf", response_class=HTMLResponse)
async def md_form(request: Request):
    return templates.TemplateResponse("markdown_to_pdf.html", {"request": request})

@app.post("/markdown-to-pdf")
async def md_upload(request: Request, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    input_dir = os.path.join(UPLOAD_FOLDER, task_id)
    output_dir = os.path.join(PROCESSED_FOLDER, task_id)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    input_path = os.path.join(input_dir, file.filename)
    output_path = os.path.join(output_dir, "markdown.pdf")
    with open(input_path, "wb") as f:
        f.write(await file.read())
    convert_markdown_to_pdf(input_path, output_path)
    return templates.TemplateResponse("markdown_to_pdf.html", {
        "request": request,
        "task_id": task_id,
        "file_name": "markdown.pdf"
    })

@app.get("/html-to-pdf", response_class=HTMLResponse)
async def html_form(request: Request):
    return templates.TemplateResponse("html_to_pdf.html", {"request": request})

@app.post("/html-to-pdf")
async def html_upload(request: Request, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    input_dir = os.path.join(UPLOAD_FOLDER, task_id)
    output_dir = os.path.join(PROCESSED_FOLDER, task_id)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    input_path = os.path.join(input_dir, file.filename)
    output_path = os.path.join(output_dir, "html.pdf")
    with open(input_path, "wb") as f:
        f.write(await file.read())
    convert_html_to_pdf(input_path, output_path)
    return templates.TemplateResponse("html_to_pdf.html", {
        "request": request,
        "task_id": task_id,
        "file_name": "html.pdf"
    })

@app.get("/convert-image-format", response_class=HTMLResponse)
async def image_format_form(request: Request):
    return templates.TemplateResponse("image_format.html", {"request": request})

@app.post("/convert-image-format")
async def image_format_upload(request: Request, file: UploadFile = File(...), format: str = Form(...)):
    task_id = str(uuid.uuid4())
    input_dir = os.path.join(UPLOAD_FOLDER, task_id)
    output_dir = os.path.join(PROCESSED_FOLDER, task_id)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    input_path = os.path.join(input_dir, file.filename)
    ext = format.lower()
    output_path = os.path.join(output_dir, f"converted.{ext}")
    with open(input_path, "wb") as f:
        f.write(await file.read())
    convert_image_format(input_path, output_path, ext)
    return templates.TemplateResponse("image_format.html", {
        "request": request,
        "task_id": task_id,
        "file_name": f"converted.{ext}"
    })

@app.get("/resize-image", response_class=HTMLResponse)
async def image_resize_form(request: Request):
    return templates.TemplateResponse("image_resize.html", {"request": request})

@app.post("/resize-image")
async def image_resize_upload(
    request: Request,
    file: UploadFile = File(...),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    scale: Optional[float] = Form(None)
):
    from utils import resize_image 
    task_id = str(uuid.uuid4())
    input_dir = os.path.join(UPLOAD_FOLDER, task_id)
    output_dir = os.path.join(PROCESSED_FOLDER, task_id)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    input_path = os.path.join(input_dir, file.filename)
    output_path = os.path.join(output_dir, "resized.png")
    with open(input_path, "wb") as f:
        f.write(await file.read())
    try:
        resize_image(input_path, output_path, width=width, height=height, scale=scale)
        return templates.TemplateResponse("image_resize.html", {
            "request": request,
            "task_id": task_id,
            "file_name": "resized.png"
        })
    except Exception as e:
        return templates.TemplateResponse("image_resize.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/download/{task_id}/{filename}")
async def download_file(task_id: str, filename: str):
    path = os.path.join(PROCESSED_FOLDER, task_id, filename)
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse("File not found", status_code=404)
