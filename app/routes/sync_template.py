from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db import get_db_connection

router = APIRouter()

# Must match CC_SITE_AUTOMATION_2025_s4m8z in Index.php _sync_template_to_automation()
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
    admin saves a template in designer.php.

    1. Updates core fields in cleverce_automation_hub.templates.
    2. Resets template_processing_queue.status → 'pending' so the
       automation pipeline re-processes the updated canvas JSON.
       Uses INSERT … ON DUPLICATE KEY UPDATE so the row is created if
       it doesn't already exist in the queue.

    If the template row doesn't exist in the automation DB at all, both
    steps are skipped silently — a missing row never breaks the CC admin
    save flow.
    """

    # ── Auth ─────────────────────────────────────────────────────────────────
    if payload.secret != SYNC_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:

            # ── 1. Check template exists in automation DB ─────────────────────
            cursor.execute("SELECT id FROM templates WHERE id = %s", (payload.id,))
            exists = cursor.fetchone()

            if not exists:
                # Template not in automation DB yet — skip silently.
                return {
                    "status": "skipped",
                    "template_id": payload.id,
                    "reason": "Template not found in automation DB",
                }

            # ── 2. Sync template fields ───────────────────────────────────────
            cursor.execute(
                """
                UPDATE templates SET
                    template_title       = %s,
                    template             = %s,
                    thumbnail            = %s,
                    large_image          = %s,
                    category             = %s,
                    template_description = %s,
                    canvas_size_id       = %s,
                    updated_on           = %s
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
                    now,
                    payload.id,
                ),
            )
            templates_affected = cursor.rowcount

            # ── 3. Reset processing queue to pending ──────────────────────────
            # UPDATE the existing row (any status: completed, processing, etc.)
            # so we never create duplicates.  If no row exists yet, INSERT one.
            cursor.execute(
                """
                UPDATE template_processing_queue
                SET    status          = 'pending',
                       last_attempt_at = %s,
                       message         = NULL
                WHERE  template_id = %s
                """,
                (now, payload.id),
            )

            if cursor.rowcount == 0:
                # No existing queue row for this template — insert fresh.
                cursor.execute(
                    """
                    INSERT INTO template_processing_queue (template_id, status, last_attempt_at, message)
                    VALUES (%s, 'pending', %s, NULL)
                    """,
                    (payload.id, now),
                )

        conn.commit()

        return {
            "status": "updated",
            "template_id": payload.id,
            "templates_rows_affected": templates_affected,
            "queue_status": "pending",
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
