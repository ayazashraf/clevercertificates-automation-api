from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import base64
import os
from app.utils.file_utils import save_image_file

router = APIRouter()

class ImageData(BaseModel):
    template_id: str
    filename: str
    image_base64: str  # should be data:image/png;base64,...

@router.post("/save-image")
async def save_image(data: ImageData):
    try:
        saved_path = save_image_file(data.template_id,data.filename, 
data.image_base64)
        return {"status": "success", "path": saved_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

