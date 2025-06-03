import subprocess
import os
from PIL import Image
import fitz  # PyMuPDF
import zipfile
import markdown2
import pdfkit



def convert_office_to_pdf(input_path, output_dir="processed"):
    command = [
        r"C:\\Program Files\\LibreOffice\\program\\soffice.exe",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path
    ]
    try:
        subprocess.run(command, check=True)
        filename = os.path.basename(input_path)
        base = os.path.splitext(filename)[0]
        return os.path.join(output_dir, f"{base}.pdf")
    except subprocess.CalledProcessError as e:
        print("Conversion failed:", e)
        return None

def convert_images_to_pdf(image_paths, output_path):
    image_list = []

    for path in image_paths:
        img = Image.open(path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        image_list.append(img)

    if image_list:
        first_image = image_list[0]
        first_image.save(output_path, save_all=True, append_images=image_list[1:])
        return output_path
    return None

def convert_pdf_to_images(pdf_path, output_dir, base_name):
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=150)
        image_filename = f"{base_name}_page_{page_num + 1}.png"
        image_path = os.path.join(output_dir, image_filename)
        pix.save(image_path)
        image_paths.append(image_path)

    zip_path = os.path.join(output_dir, f"{base_name}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for img in image_paths:
            zipf.write(img, arcname=os.path.basename(img))

    return image_paths, zip_path

def extract_images_from_pdf(pdf_path, output_dir, base_name):
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            # Handle CMYK images
            if pix.n >= 5:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            image_filename = f"{base_name}_page{page_index+1}_img{img_index+1}.png"
            image_path = os.path.join(output_dir, image_filename)
            pix.save(image_path)
            image_paths.append(image_path)
            pix = None

    zip_path = os.path.join(output_dir, f"{base_name}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for img in image_paths:
            zipf.write(img, arcname=os.path.basename(img))

    return image_paths, zip_path

WKHTMLTOPDF_PATH = r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

def convert_markdown_to_pdf(md_path, output_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html_body = markdown2.markdown(
        md_content,
        extras=["fenced-code-blocks", "tables", "strike", "code-friendly", "cuddled-lists", "metadata"]
    )

    full_html = f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body {{ font-family: Arial, sans-serif; padding: 2em; }}
          h1, h2, h3 {{ color: #333; }}
          pre, code {{ background: #f4f4f4; padding: 0.5em; border-radius: 5px; font-family: monospace; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
          ul, ol {{ padding-left: 2em; }}
        </style>
      </head>
      <body>{html_body}</body>
    </html>
    """

    pdfkit.from_string(full_html, output_path, configuration=PDFKIT_CONFIG)
    return output_path



def convert_html_to_pdf(html_path, output_path):
    pdfkit.from_file(html_path, output_path, configuration=PDFKIT_CONFIG, options={
    'enable-local-file-access': None,
    'quiet': '',
    'no-stop-slow-scripts': '',
    'load-error-handling': 'ignore',})
    return output_path

def convert_image_format(input_path, output_path, output_format):
    img = Image.open(input_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Normalize JPG → JPEG
    pil_format = "JPEG" if output_format.lower() == "jpg" else output_format.upper()

    img.save(output_path, format=pil_format)
    return output_path
