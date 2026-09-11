from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.db import get_cc_db_connection

router = APIRouter()

@router.get("/get-template-details")
async def get_template_details(template_id: int):
    """
    Fetch template canvas data from cc_live (the source-of-truth DB).

    Previously queried cleverce_automation_hub.templates, which only contains
    templates that have been through the admin sync flow. New templates created
    in the admin but not yet resaved via sync were invisible to the generator.
    Querying cc_live directly means any template — draft or live — is accessible
    as soon as it exists, without requiring a separate sync step.
    """
    try:
        conn = get_cc_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.id, t.template_title, t.display_title, t.template,
                       t.thumbnail, t.large_image, t.category, t.canvas_size_id,
                       t.is_deleted, t.live,
                       cs.width, cs.height
                FROM templates t
                JOIN canvas_size cs ON t.canvas_size_id = cs.id
                WHERE t.id = %s AND t.is_deleted = 0
            """, (template_id,))
            result = cursor.fetchone()
        conn.close()
        if result:
            return result
        else:
            return JSONResponse(status_code=404, content={"error": "Template not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

