from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from app.utils.pdf_utils import generate_instruction_pdfs

router = APIRouter()

@router.post("/generate-access-pdfs")
async def generate_access_pdfs(
    template_id: int = Form(...),
    template_title: str = Form(...)
):
    try:
        generate_instruction_pdfs(template_id, template_title)
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
