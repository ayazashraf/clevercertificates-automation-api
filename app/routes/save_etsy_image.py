from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.file_utils import save_image_file

router = APIRouter()

class EtsyImageData(BaseModel):
    template_id: str
    filename: str
    image_base64: str  # should be data:image/png;base64,...

# Dedicated upload endpoint for branded Etsy listing images, kept separate
# from /save-image so these marketing/listing assets are clearly identifiable
# (in logs and storage) from normal certificate image generation, per the
# "Generate Protected Etsy Listing Images" requirement. Reuses the existing
# save_image_file pipeline rather than introducing new storage logic.
@router.post("/save-etsy-image")
async def save_etsy_image(data: EtsyImageData):
    try:
        saved_path = save_image_file(data.template_id, data.filename, data.image_base64)
        return {"status": "success", "path": saved_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

__all__ = ["router"]
