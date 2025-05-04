from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import JSONResponse
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

@router.post("/save-image-with-frame")
async def save_image_with_frame(template_id: int, filename: str = "preview-with-frame", image_base64: str = Form(...)):
    try:
        saved_path = save_image_file(template_id, filename, image_base64)
        return JSONResponse(content={"message": "Image with frame saved", "path": saved_path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/save-image-zoomed")
async def save_image_zoomed(template_id: int, filename: str = "preview-zoomed", image_base64: str = Form(...)):
    try:
        saved_path = save_image_file(template_id, filename, image_base64)
        return JSONResponse(content={"message": "Zoomed image saved", "path": saved_path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/save-image-on-table")
async def save_image_on_table(template_id: int, filename: str = "preview-on-table", image_base64: str = Form(...)):
    try:
        saved_path = save_image_file(template_id, filename, image_base64)
        return JSONResponse(content={"message": "Table image saved", "path": saved_path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/save-thumbnail")
async def save_thumbnail(template_id: int, filename: str = "thumbnail", image_base64: str = Form(...)):
    try:
        saved_path = save_image_file(template_id, filename, image_base64)
        return JSONResponse(content={"message": "Thumbnail image saved", "path": saved_path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

__all__ = ["router"]

