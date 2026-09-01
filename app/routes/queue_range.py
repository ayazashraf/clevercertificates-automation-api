"""
POST /queue-template-range
--------------------------
Bulk-syncs a range (or explicit list) of templates from cc_live into the
automation hub and marks each as pending in template_processing_queue.

Use this whenever templates are created directly in the DB (not through the
designer save flow) so they never trigger the individual /sync-template hook.

Examples
--------
# Sync templates 1714–1765 (range)
POST /queue-template-range
{
  "secret": "CC_SITE_AUTOMATION_2025_s4m8z",
  "start_id": 1714,
  "end_id": 1765
}

# Sync a specific list of IDs (overrides range when provided)
POST /queue-template-range
{
  "secret": "CC_SITE_AUTOMATION_2025_s4m8z",
  "ids": [1714, 1715, 1720]
}

Response
--------
{
  "status": "done",
  "synced": 47,           # upserted into automation hub templates table
  "queued": 47,           # inserted / reset to pending in queue
  "skipped": 3,           # live=0 or is_deleted=1 in cc_live — skipped
  "not_found": 1,         # IDs in range not in cc_live at all
  "ids_queued": [1714, ...]
}
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db import get_db_connection, get_cc_db_connection

router = APIRouter()

SYNC_SECRET = "CC_SITE_AUTOMATION_2025_s4m8z"


# ─────────────────────────────────────────────────────────────────────────────
# GET /queue-templates-now?start_id=1714&end_id=1765&secret=...
#
# Lightweight version for templates ALREADY in the automation hub DB.
# Just resets / inserts their queue rows to 'pending' — no cc_live sync.
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/queue-templates-now")
def queue_templates_now(
    secret: str,
    start_id: Optional[int] = None,
    end_id:   Optional[int] = None,
):
    if secret != SYNC_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if start_id is None or end_id is None:
        raise HTTPException(status_code=400, detail="Provide start_id and end_id")
    if start_id > end_id:
        raise HTTPException(status_code=400, detail="start_id must be <= end_id")

    id_list = list(range(start_id, end_id + 1))
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    hub_conn = get_db_connection()
    queued   = []
    missing  = []

    try:
        placeholders = ", ".join(["%s"] * len(id_list))
        with hub_conn.cursor() as hub:

            # Check which IDs actually exist in the automation hub
            hub.execute(
                f"SELECT id FROM templates WHERE id IN ({placeholders})",
                tuple(id_list),
            )
            found_ids = {r["id"] for r in hub.fetchall()}
            missing   = [i for i in id_list if i not in found_ids]

            # Insert or reset each found template to pending
            for tid in found_ids:
                hub.execute(
                    """
                    INSERT INTO template_processing_queue
                        (template_id, status, last_attempt_at, message)
                    VALUES (%s, 'pending', %s, NULL)
                    ON DUPLICATE KEY UPDATE
                        status          = 'pending',
                        last_attempt_at = %s,
                        message         = NULL
                    """,
                    (tid, now, now),
                )
                queued.append(tid)

        hub_conn.commit()

    except Exception as e:
        hub_conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        hub_conn.close()

    return {
        "status":      "done",
        "queued":      len(queued),
        "missing_from_hub": len(missing),
        "ids_queued":  sorted(queued),
        "ids_missing": sorted(missing),
    }


class QueueRangeRequest(BaseModel):
    secret: str
    start_id: Optional[int] = None
    end_id:   Optional[int] = None
    ids:      Optional[List[int]] = None   # explicit list overrides range


@router.post("/queue-template-range")
def queue_template_range(payload: QueueRangeRequest):

    # ── Auth ──────────────────────────────────────────────────────────────────
    if payload.secret != SYNC_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ── Build the ID list ─────────────────────────────────────────────────────
    if payload.ids:
        id_list = sorted(set(payload.ids))
    elif payload.start_id is not None and payload.end_id is not None:
        if payload.start_id > payload.end_id:
            raise HTTPException(status_code=400, detail="start_id must be <= end_id")
        id_list = list(range(payload.start_id, payload.end_id + 1))
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either start_id+end_id or ids[]"
        )

    if not id_list:
        raise HTTPException(status_code=400, detail="ID list is empty")

    # ── Fetch templates from cc_live ──────────────────────────────────────────
    cc_conn  = get_cc_db_connection()
    hub_conn = get_db_connection()

    synced    = []
    skipped   = []
    not_found = []

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    try:
        placeholders = ", ".join(["%s"] * len(id_list))

        with cc_conn.cursor() as cc:
            cc.execute(
                f"""
                SELECT id, template_title, template, thumbnail, large_image,
                       category, template_description, canvas_size_id,
                       live, is_deleted
                FROM templates
                WHERE id IN ({placeholders})
                """,
                tuple(id_list),
            )
            rows = cc.fetchall()

        found_ids = {r["id"] for r in rows}

        # IDs that don't exist in cc_live at all
        not_found = [i for i in id_list if i not in found_ids]

        # IDs that exist but are draft/deleted — skip them
        for row in rows:
            if row["is_deleted"] or not row["live"]:
                skipped.append(row["id"])

        live_rows = [r for r in rows if not r["is_deleted"] and r["live"]]

        # ── Upsert into automation hub + queue ────────────────────────────────
        with hub_conn.cursor() as hub:
            for row in live_rows:
                tid = row["id"]

                # 1. Upsert into automation hub templates table
                hub.execute(
                    """
                    INSERT INTO templates
                        (id, template_title, template, thumbnail, large_image,
                         category, template_description, canvas_size_id,
                         updated_on)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        template_title       = VALUES(template_title),
                        template             = VALUES(template),
                        thumbnail            = VALUES(thumbnail),
                        large_image          = VALUES(large_image),
                        category             = VALUES(category),
                        template_description = VALUES(template_description),
                        canvas_size_id       = VALUES(canvas_size_id),
                        updated_on           = VALUES(updated_on)
                    """,
                    (
                        tid,
                        row["template_title"],
                        row["template"],
                        row["thumbnail"],
                        row["large_image"],
                        row["category"],
                        row["template_description"],
                        row["canvas_size_id"],
                        now,
                    ),
                )

                # 2. Insert or reset queue row to pending
                hub.execute(
                    """
                    INSERT INTO template_processing_queue
                        (template_id, status, last_attempt_at, message)
                    VALUES (%s, 'pending', %s, NULL)
                    ON DUPLICATE KEY UPDATE
                        status          = 'pending',
                        last_attempt_at = %s,
                        message         = NULL
                    """,
                    (tid, now, now),
                )

                synced.append(tid)

        hub_conn.commit()

    except Exception as e:
        hub_conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cc_conn.close()
        hub_conn.close()

    return {
        "status":    "done",
        "synced":    len(synced),
        "queued":    len(synced),
        "skipped":   len(skipped),
        "not_found": len(not_found),
        "ids_queued":   synced,
        "ids_skipped":  skipped,   # live=0 or deleted
        "ids_not_found": not_found,  # not in cc_live at all
    }
