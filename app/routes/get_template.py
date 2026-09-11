from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.db import get_db_connection

router = APIRouter()


@router.get("/get-template-details")
async def get_template_details(template_id: int):
    """
    Fetch template canvas data from cleverce_automation_hub (localhost).

    Templates are synced here via /sync-template when saved in the admin
    designer, and new draft templates are also present in this DB.
    Querying localhost is fast (<1s); the previous version queried the remote
    cc_live DB which caused ~60s delays.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.id, t.template_title, t.display_title, t.template,
                       t.thumbnail, t.large_image, t.category, t.canvas_size_id,
                       t.is_deleted, cs.width, cs.height
                FROM templates t
                JOIN canvas_size cs ON t.canvas_size_id = cs.id
                WHERE t.id = %s AND t.is_deleted = 0
            """, (template_id,))
            result = cursor.fetchone()
        conn.close()

        if result:
            return result
        return JSONResponse(status_code=404, content={"error": "Template not found"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
