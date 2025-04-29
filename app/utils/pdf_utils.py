from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
import os

def generate_instruction_pdfs(template_id: int, template_title: str):
    base_dir =f"/home/cleverce/content-management-files.clevercertificates.com/items/{template_id}"
    os.makedirs(base_dir, exist_ok=True)

    template_slug = template_title.lower().replace(" ", "-")
    editor_link =f"https://www.clevercertificates.com/template-designer/{template_slug}?code=[your-code]"

    static_lines = [
        "How to Access Your Editable Certificate",
        "Step 2: Enter your Order Number, Email Address, and Order Date.",
        "Step 3: If your order is found, you'll receive an Order Code.",
        "Step 4: Open the link format below and replace [your-code] with the code:", editor_link,
        "Step 5: Paste the completed link into a desktop or laptop browser to start editing.",
        "Note: The Order Code will appear in red text.",
        "Check your email (including spam/junk folders) if you do not see the code immediately.",
        "Need Help? You can message us directly or email us at support@clevercertificates.com for assistance."
    ]

    def create_pdf(filepath: str, step_1_url: str):
        c = canvas.Canvas(filepath, pagesize=LETTER)
        width, height = LETTER
        y = height - inch
        c.setFont("Helvetica", 11)
        c.drawString(inch, y, static_lines[0])
        y -= 0.5 * inch
        c.drawString(inch, y, f"Step 1: Go to {step_1_url}")
        for line in static_lines[1:]:
            y -= 0.3 * inch
            c.drawString(inch, y, line)
        c.save()

    etsy_path = os.path.join(base_dir,f"{template_id}_etsy_access_instructions.pdf")
    gumroad_path = os.path.join(base_dir,f"{template_id}_gumroad_access_instructions.pdf")

    create_pdf(etsy_path,"https://www.clevercertificates.com/etsy-access")
    create_pdf(gumroad_path,"https://www.clevercertificates.com/gumroad-access")

    return {
        "etsy_pdf": etsy_path,
        "gumroad_pdf": gumroad_path
    }
