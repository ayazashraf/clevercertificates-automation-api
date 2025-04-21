import base64
import os

def save_image_file(template_id: str, filename: str, image_data_url: 
str) -> str:
    if not image_data_url.startswith("data:image"):
        raise ValueError("Invalid image format")

    header, encoded = image_data_url.split(",", 1)
    extension = header.split('/')[1].split(';')[0]
    raw_data = base64.b64decode(encoded)

    # New folder path based on template_id
    base_path = 
"/home/cleverce/content-management-files.clevercertificates.com/items"
    template_path = os.path.join(base_path, template_id, "media", 
"images")
    os.makedirs(template_path, exist_ok=True)

    filename = f"{filename}.{extension}"
    full_path = os.path.join(template_path, filename)

    with open(full_path, "wb") as f:
        f.write(raw_data)

    # Return the public URL path
    return 
f"https://content-management-files.clevercertificates.com/items/{template_id}/media/images/{filename}"

