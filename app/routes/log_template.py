from fastapi import APIRouter, Form
from app.db import get_db_connection
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.post("/log-template-processing")
async def log_template_processing(
    template_id: int = Form(...),
    status: str = Form(...),
    message: str = Form("")
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO template_processing_logs (template_id, status, 
message, generated_at)
            VALUES (%s, %s, %s, %s)
        """, (template_id, status, message, datetime.now()))

        conn.commit()
        cursor.close()
        conn.close()

        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

