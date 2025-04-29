import pymysql.cursors

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="cleverce_automation_hub_user",
        password="fm75r8*KW=,o",
        database="cleverce_automation_hub",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
