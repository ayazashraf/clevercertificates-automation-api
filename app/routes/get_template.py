from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.db import get_db_connection

router = APIRouter()

@router.get("/get-template-details")
async def get_template_details(template_id: int):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.*, cs.width, cs.height, t.canvas_size_id
                FROM templates t
                JOIN canvas_size cs ON t.canvas_size_id = cs.id
                WHERE t.id = %s AND t.is_deleted = 0
            """, (template_id,))
            result = cursor.fetchone()
        conn.close()
        if result:
            return result
        else:
            
            return JSONResponse(status_code=404, content={"error":"Template not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

