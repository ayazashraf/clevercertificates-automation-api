from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db import get_db_connection

router = APIRouter()

# Must match CC_AUTOMATION_SYNC_SECRET in Index.php
SYNC_SECRET = "CC_SITE_AUTOMATION_2025_s4m8z"


class TemplateSyncPayload(BaseModel):
    secret: str
    id: int
    template_title: str
    template: str                       # canvas JSON (longtext)
    thumbnail: str
    large_image: Optional[str] = None
    category: int
    template_description: Optional[str] = None
    canvas_size_id: int


@router.post("/sync-template")
def sync_template(payload: TemplateSyncPayload):
    """
    Called by the CC main site (Index.php / update_template) whenever an
    admin saves a template in designer.php.  Mirrors the core fields to the
    cleverce_automation_hub.templates row so the automation pipeline always
    has the latest canvas JSON, thumbnail, and metadata.
    """

    # ── Auth ────────────────────────────────────────────────────────────────
    if payload.secret != SYNC_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check row exists — automation DB may not have every template yet
            cursor.execute("SELECT id FROM templates WHERE id = %s", (payload.id,))
            exists = cursor.fetchone()

            if exists:
                cursor.execute(
                    """
                    UPDATE templates SET
                        template_title      = %s,
                        template            = %s,
                        thumbnail           = %s,
                        large_image         = %s,
                        category            = %s,
                        template_description= %s,
                        canvas_size_id      = %s,
                        updated_on          = %s
                    WHERE id = %s
                    """,
                    (
                        payload.template_title,
                        payload.template,
                        payload.thumbnail,
                        payload.large_image,
                        payload.category,
                        payload.template_description,
                        payload.canvas_size_id,
                        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        payload.id,
                    ),
                )
                conn.commit()
                affected = cursor.rowcount
                return {
                    "status": "updated",
                    "template_id": payload.id,
                    "rows_affected": affected,
                }
            else:
                # Template doesn't exist in automation DB yet — skip silently
                # so a missing row never breaks the CC admin save flow.
                return {
                    "status": "skipped",
                    "template_id": payload.id,
                    "reason": "Template not found in automation DB",
                }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
