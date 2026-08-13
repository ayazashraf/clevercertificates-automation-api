from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
import os

def generate_instruction_pdfs(template_id: int, template_title: str):
    base_dir =f"/home/cleverce/content-management-files.clevercertificates.com/items/{template_id}"
    os.makedirs(base_dir, exist_ok=True)

    access_url = "https://www.clevercertificates.com/etsy-access"

    # Kept in sync with the live /etsy-access page (EtsyAccessController +
    # views/pages/etsy_access.php in the main Clever-Certificates-V3 app) and
    # the Etsy automated email. On a successful search, that page auto-fills
    # ready-to-click Full/Lite editor links itself — customers don't
    # manually enter or copy an order code in the normal path, so this PDF
    # shouldn't imply that step either. An order code is only ever shown as
    # a fallback message if a match can't be linked immediately.
    #
    # Each entry is (text, font, font_size). Plain strings default to
    # Helvetica 11 (see create_pdf below).
    static_lines = [
        "How to Access & Edit Your Certificate",
        "Step 2: Enter your Etsy Order Number, Email Address, and Order Date, then",
        "click \"Find My Order\".",
        "  • Use the exact email address on your Etsy account and the date from",
        "    your Etsy purchase confirmation.",
        "",
        "Step 3: Choose your editor — both links appear automatically once your",
        "order is found:",
        ("Full Design Editor — Your main editor", "Helvetica-Bold", 11),
        "  • Full canvas control. Re-download anytime with the same link —",
        "    no sessions are used.",
        "  • Desktop or laptop only (Windows or Mac). If the editor appears",
        "    blank, refresh the page once.",
        "  • Complete all edits before downloading, printing, or sharing —",
        "    it locks to your last saved version once used.",
        ("Lite Editor — Optional", "Helvetica-Bold", 11),
        "  • A simpler, form-based editor.",
        "  • Works on any device — phone, tablet, desktop, or laptop.",
        "  • Uses 1 edit session per download — check your remaining",
        "    sessions before proceeding.",
        "",
        "Can't find your order? Double-check your Order Number, email, and date.",
        "If it still can't be found, we'll show your order code on the page and",
        "email you the editor link shortly.",
        "",
        "Need Help? You can message us directly or email us at support@clevercertificates.com for assistance."
    ]

    def create_pdf(filepath: str, step_1_url: str):
        c = canvas.Canvas(filepath, pagesize=LETTER)
        width, height = LETTER
        y = height - inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y, static_lines[0])
        y -= 0.4 * inch
        c.setFont("Helvetica", 11)
        c.drawString(inch, y, f"Step 1: Go to {step_1_url}")
        for line in static_lines[1:]:
            y -= 0.3 * inch
            if isinstance(line, tuple):
                text, font, size = line
                c.setFont(font, size)
                c.drawString(inch, y, text)
                c.setFont("Helvetica", 11)
            else:
                c.drawString(inch, y, line)
        c.save()

    etsy_path = os.path.join(base_dir,f"{template_id}_etsy_access_instructions.pdf")

    create_pdf(etsy_path, access_url)

    # Gumroad instructional PDF generation is intentionally disabled — no
    # Gumroad access PDF should be produced for any item. The helper above
    # is left generic/reusable in case Gumroad instructions are needed again
    # in the future; simply re-enable the two lines below to restore it.
    # gumroad_path = os.path.join(base_dir, f"{template_id}_gumroad_access_instructions.pdf")
    # create_pdf(gumroad_path, "https://www.clevercertificates.com/gumroad-access")

    return {
        "etsy_pdf": etsy_path
    }
