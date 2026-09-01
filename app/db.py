import os
import pymysql.cursors

def get_db_connection():
    """Automation hub DB (cleverce_automation_hub)."""
    return pymysql.connect(
        host="localhost",
        user="cleverce_automation_hub_user",
        password="fm75r8*KW=,o",
        database="cleverce_automation_hub",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

def get_cc_db_connection():
    """Main CC site DB (cc_live) — credentials via env vars."""
    return pymysql.connect(
        host=os.environ.get("CC_DB_HOST", "localhost"),
        user=os.environ.get("CC_DB_USER", "root"),
        password=os.environ.get("CC_DB_PASSWORD", ""),
        database=os.environ.get("CC_DB_NAME", "cc_live"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
