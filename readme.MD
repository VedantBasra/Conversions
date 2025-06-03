# FastAPI File Converter

A powerful and lightweight file conversion web app built with **FastAPI** and **Jinja2** — designed to convert documents, images, and HTML/Markdown into PDFs, extract and manipulate images from PDFs, and more.

---

## 🚀 Features

| Feature                      | Description                                 |
|------------------------------|---------------------------------------------|
| DOCX to PDF                  | Convert Word documents to PDF               |
| PPTX to PDF                  | Convert PowerPoint slides to PDF            |
| XLSX to PDF                  | Convert Excel spreadsheets to PDF           |
| Images to PDF                | Merge multiple images into a single PDF     |
| PDF to Images                | Convert PDF pages to individual PNGs        |
| Extract Images from PDF      | Extract embedded images from PDF            |
| Markdown to PDF              | Convert `.md` files into styled PDF         |
| HTML to PDF                  | Convert `.html` pages into styled PDF       |
| Image Format Converter       | Convert between JPG, PNG, WEBP              |
| Image Resizer                | Resize images by width/height or scale      |

---

## 🖥️ Run Locally

```bash
# Clone the repo
git clone https://github.com/yourname/fastapi-file-converter.git
cd fastapi-file-converter

# Set up virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the app
uvicorn main:app --reload
```

Then open your browser to:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📁 Project Structure

```
.
├── main.py                   # FastAPI routes
├── utils.py                  # Core conversion logic
├── templates/                # Jinja2 + TailwindCSS HTML
├── uploads/                  # Temp storage (per-task)
├── processed/                # Output storage (per-task)
├── requirements.txt
└── README.md
```

---

## 🧰 Requirements

You must have these installed:

- **Python 3.9+**
- **LibreOffice** for converting `.docx`, `.pptx`, `.xlsx`  
- **wkhtmltopdf** for HTML and Markdown to PDF conversion

> You may need to adjust the paths to `soffice.exe` and `wkhtmltopdf.exe` in `utils.py`.

---

## 📜 License

MIT

---
