from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.db import get_db_connection

router = APIRouter()

class VariantItem(BaseModel):
    id: int
    endpoint: str
    filename: str

class BatchResponse(BaseModel):
    initial_template_id: int
    variants: List[VariantItem]

@router.get("/get-template-batch", response_model=BatchResponse)
def get_template_batch():
    conn = None
    cursor = None
    try:
        # Use shared app DB connection
        conn = get_db_connection()        

        # Step 1: Get first pending template
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT template_id FROM template_processing_queue
                WHERE status = 'pending' AND template_id IN (
                SELECT id FROM templates WHERE live = 1 AND is_deleted = 0
                )
                ORDER BY id ASC
                LIMIT 5
            """)
            row = cursor.fetchone()
         

        if not row:
            raise HTTPException(status_code=404, detail="No pending templates found")

        template_id = row['template_id']

        # Step 2: Mark it as processing
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE template_processing_queue
                SET status = 'processing', last_attempt_at = NOW()
                WHERE template_id = %s
            """, (template_id,))                    
            conn.commit()

        # Step 3: Define variant IDs (hardcoded logic for now)
        variants = [
            {"id": 1553, "endpoint": "/save-image-with-frame", "filename": "preview-with-frame-wm"},
            {"id": 1552, "endpoint": "/save-image-zoomed", "filename": "preview-zoomed-wm"},
            {"id": 1551, "endpoint": "/save-image-on-table", "filename": "preview-on-table-wm"}
        ]

        return BatchResponse(initial_template_id=template_id, variants=variants)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@router.post("/mark-template-completed")
def mark_template_completed(template_id: int):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE template_processing_queue
            SET status = 'completed', last_attempt_at = NOW(), message = NULL
            WHERE template_id = %s
        """, (template_id,))
        conn.commit()

        return {"status": "ok", "template_id": template_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()