from fastapi import APIRouter, HTTPException, Query
from app.db import get_db_connection
from app.services.gemini_service import generate_market_data
import pymysql
import re
import asyncio
import requests
import time

router = APIRouter()

@router.post("/generate-market-data/{template_id}")
async def generate_market_data_api(template_id: int):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT t.*, c.name AS category_name, tk.keywords
                FROM templates t
                JOIN categories c ON c.id = t.category
                LEFT JOIN template_keywords tk ON tk.template_id = t.id
                WHERE t.id = %s
            """, (template_id,))
            template = cursor.fetchone()

            if not template:
                raise HTTPException(status_code=404, detail="Template not found.")

            await process_template(template, cursor)
            db.commit()

        return {"success": True, "message": f"Template ID {template_id} processed successfully."}

    except pymysql.MySQLError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"MySQL Error: {str(e)}")
    finally:
        db.close()

@router.post("/generate-market-data-batch")
async def generate_market_data_batch(limit: int = Query(10, description="Number of templates to process")):
    db = get_db_connection()
    processed = []
    skipped = []

    try:
        with db.cursor() as cursor:
            cursor.execute(f"""
                SELECT t.*, c.name AS category_name, tk.keywords
                FROM templates t
                JOIN categories c ON c.id = t.category
                LEFT JOIN template_keywords tk ON tk.template_id = t.id
                WHERE t.live = 1 AND t.is_deleted = 0
                  AND t.id NOT IN (SELECT template_id FROM template_market_data)
                LIMIT %s
            """, (limit,))
            templates = cursor.fetchall()

            if not templates:
                raise HTTPException(status_code=404, detail="No templates found to process.")

            for template in templates:
                try:
                    await process_template(template, cursor)
                    processed.append(template["id"])
                    await asyncio.sleep(2)  # Optional: 2 seconds pause between templates
                except Exception as e:
                    skipped.append({"id": template["id"], "error": str(e)})

            db.commit()

        return {
            "success": True,
            "processed_ids": processed,
            "skipped": skipped
        }

    except pymysql.MySQLError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"MySQL Error: {str(e)}")
    finally:
        db.close()

async def process_template(template: dict, cursor):
    from app.services.gemini_service import generate_market_data

    generated = await generate_market_data(template)
    gumroad_url = re.sub(r'[^a-zA-Z0-9]+', '-', template["template_title"]).lower().strip('-')
    quantity = 999
    sku = f"CC-{template['id']}"

    # Predefined text blocks
    etsy_extra = """✅ Instant Digital Access – No Canva, No Sign-Up Required
✅ No software or fonts required
✅ Edit directly in your browser (no software needed)
✅ Download as PDF, PNG, JPG, or SVG
✅ Print at home or send to a print shop
✅ No watermark or branding on the final certificate

🔽 Download & Share Options:
With your purchase, you can choose from the following high-resolution formats:
• PDF – Best for professional printing
• PNG & JPG – Great for both digital and print use
• SVG – Image wrapped in scalable format (not layered or cuttable)
• Share – Instantly on Facebook, Pinterest, or via Email
🔁 Each download or share counts as one use. Multiple uses require additional quantity or a membership.
________________________________________

🥋 WHAT’S INCLUDED
• Template (US Letter – 11" x 8.5")
• Easy access PDF with secure editor link
• Fully editable online – no installation, no login
• Optional Add-On if you'd like us to customize it for you
• Bonus design graphics from Clever Certificates
________________________________________

✏️ YOU CAN CUSTOMIZE
• All text: title, name, rank, date, instructor name, etc.
• Fonts, colors, and placement
• Add your own logo, seal, or images
• Change borders or background
• Download as PDF, PNG, JPG, or SVG for high-res printing or digital delivery
• Share via email, Facebook, Pinterest, or print anywhere
________________________________________

⚙️ HOW IT WORKS
1. Purchase the listing
2. Download the attached PDF with your access link
3. Open the link in any browser (desktop/laptop recommended)
4. Customize your certificate easily
5. Download, print, or share digitally
Each purchase includes one completed download or share. Reuse requires a new purchase or an add-on license.
________________________________________

🛠️ OPTIONAL CUSTOMIZATION
Need help editing your certificate?
👉 Add our Customization Service from our shop and we’ll do it for you.
🔗 https://www.etsy.com/listing/1885731252/add-on-professional-customization
________________________________________

⚠️ IMPORTANT NOTES
• This is a digital product only – nothing physical will be shipped
• Best experience is on desktop/laptop
• Colors may vary depending on your screen/printer
• Page size and orientation are fixed (US Letter landscape)
________________________________________

📜 TERMS OF USE
• For personal use or internal organizational awarding only
• Resale, redistribution, or sharing is not allowed
• Digital purchases are non-refundable once accessed or downloaded
________________________________________

🔥 Thank you for choosing Clever Certificates – trusted by educators, instructors, and event organizers worldwide! 🔥"""

    gumroad_extra = """✅ Edit online instantly

✅ No software or fonts required

✅ Download as PDF, PNG, JPG, or SVG

✅ Print at home or send to a print shop

✅ Great for dojos, martial arts academies, and training events

🔽 Download & Share Options:
With your purchase, you can choose from the following high-resolution formats:
• PDF – Best for professional printing
• PNG & JPG – Great for both digital and print use
• SVG – Image wrapped in scalable format (not layered or cuttable)
• Share – Instantly on Facebook, Pinterest, or via Email
🔁 Each download or share counts as one use. Multiple uses require additional quantity or a membership.
________________________________________

🥋 WHAT’S INCLUDED
• Karate Black Belt Certificate Template (US Letter – 11" x 8.5")
• Easy access PDF with secure editor link
• Fully editable online – no installation, no login
• Optional Add-On if you'd like us to customize it for you
• Bonus design graphics from Clever Certificates
________________________________________

✏️ YOU CAN CUSTOMIZE
• All text: title, name, rank, date, instructor name, etc.
• Fonts, colors, and placement
• Add your own logo, seal, or images
• Change borders or background
• Download as PDF, PNG, JPG, or SVG for high-res printing or digital delivery
• Share via email, Facebook, Pinterest, or print anywhere
________________________________________

⚙️ HOW IT WORKS
1. Purchase the listing
2. Download the attached PDF with your access link
3. Open the link in any browser (desktop/laptop recommended)
4. Customize your certificate easily
5. Download, print, or share digitally
Each purchase includes one completed download or share. Reuse requires a new purchase or an add-on license.
________________________________________

🛠️ OPTIONAL CUSTOMIZATION
Need help editing your certificate?
👉 Add our Customization Service from our shop and we’ll do it for you.
________________________________________

⚠️ IMPORTANT NOTES
• This is a digital product only – nothing physical will be shipped
• Best experience is on desktop/laptop
• Colors may vary depending on your screen/printer
• Page size and orientation are fixed (US Letter landscape)
________________________________________

📜 TERMS OF USE
• For personal use or internal organizational awarding only
• Resale, redistribution, or sharing is not allowed
• Digital purchases are non-refundable once accessed or downloaded
________________________________________

🔥 Thank you for choosing Clever Certificates – trusted by educators, instructors, and event organizers worldwide! 🔥"""

    # Merge generated paragraph + predefined extras
    full_etsy_description = f"{generated['paragraph']}\n\n{etsy_extra}"
    full_gumroad_description = f"{generated['paragraph']}\n\n{gumroad_extra}"

    sql = """
    INSERT INTO template_market_data 
    (template_id, original_price, etsy_title, generated_summary, generated_paragraph, gumroad_url_slug, etsy_tags, etsy_materials, alt_text_primary, alt_text_secondary, alt_text_third, alt_text_fourth, etsy_quantity, etsy_sku, gumroad_description, etsy_description, etsy_section, gumroad_name, gumroad_summary)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        template["id"],
        template["original_price"],
        generated["etsy_title"],
        generated["summary"],
        generated["paragraph"],
        gumroad_url,
        generated["tags"],
        generated["materials"],
        generated["alt_primary"],
        generated["alt_secondary"],
        generated["alt_third"],
        generated["alt_fourth"],
        quantity,
        sku,
        full_gumroad_description,
        full_etsy_description,
        template["category_name"],
        generated["etsy_title"],        
        generated["summary"]
    ))


@router.get("/get-next-template-to-process")
def get_next_template():
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id
                FROM templates
                WHERE live = 1
                  AND is_deleted = 0
                  AND id NOT IN (SELECT template_id FROM template_market_data)
                ORDER BY id ASC
                LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                return {"template_id": result["id"]}
            else:
                return {"template_id": None}
    finally:
        db.close()
