from PIL import Image
import base64
import os
from io import BytesIO

def save_image_file(template_id: str, filename: str, image_data_url: 
str) -> str:
    if not image_data_url.startswith("data:image"):
        raise ValueError("Invalid image format")

    header, encoded = image_data_url.split(",", 1)
    extension = header.split('/')[1].split(';')[0]
    raw_data = base64.b64decode(encoded)

    # New folder path based on template_id
    base_path = "/home/cleverce/content-management-files.clevercertificates.com/items"
    template_path = os.path.join(base_path, str(template_id), 
"media","images")
    os.makedirs(template_path, exist_ok=True)

    filename = f"{filename}.{extension}"
    full_path = os.path.join(template_path, filename)

    with open(full_path, "wb") as f:
        f.write(raw_data)

    # Return the public URL path
    return "https://content-management-files.clevercertificates.com/items/{template_id}/media/images/{filename}"

def save_pdf_file(template_id, filename, image_base64):
    base_path = f"/home/cleverce/content-management-files.clevercertificates.com/items/{template_id}/media"
    os.makedirs(base_path, exist_ok=True)

    # Decode base64
    header, encoded = image_base64.split(",", 1)
    image_data = base64.b64decode(encoded)

    # Load into Pillow
    image = Image.open(BytesIO(image_data)).convert("RGB")

    # Save as PDF
    pdf_path = os.path.join(base_path, f"{filename}.pdf")
    image.save(pdf_path, "PDF", resolution=300.0)

    return pdf_path
