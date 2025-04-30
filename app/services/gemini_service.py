import httpx
import re

GEMINI_API_KEY = "AIzaSyDw2V62GQeeaaCu2DAAqGMjmgzzDh5ALB0"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

async def call_gemini(prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(GEMINI_API_URL, json=payload)
        data = response.json()
        text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        return text.strip()

async def generate_market_data(template: dict):
    title = template["template_title"]
    keywords = template.get("keywords", "")
    keywordText = f" Use keywords like {keywords}." if keywords else ""

    prompts = {
        "etsy_title": f"Write one Etsy product title (maximum 140 characters including spaces) an editable and printable certificate template titled '{title}'. Provide only one title, no multiple options, no explanation.",
        "summary": f"Write one short SEO-optimized summary (15-20 words) an editable and printable certificate template titled '{title}'. Provide only one clean summary without extra options.",
        "paragraph": f"Write one compelling Etsy product description (50-60 words) an editable and printable certificate template titled '{title}'. Provide only one paragraph without extra suggestions.",
        "tags": f"Generate exactly 13 Optimized Etsy SEO tags for an editable and printable certificate template titled '{title}'(each maximum 20 characters, comma-separated). Return only tags separated by commas.",
        "materials": f"Generate exactly 13 material for digital template titled '{title}' (each maximum 20 characters, comma-separated) . Return only keywords, no explanation.",
        "alt_primary": f"Write one SEO-friendly Alt text (300–450 characters) an editable and printable certificate template titled '{title}'. Mention design details, style, and usage purpose naturally. Provide only one paragraph without extra suggestions.",
        "alt_secondary": f"Create one Etsy-optimized Alt text (300–450 characters) an editable and printable certificate template titled '{title}'. Focus on audience (buyers) and best use case.  Provide only one paragraph without extra suggestions.",
        "alt_third": f"Suggest one SEO-optimized Alt text (300–450 characters) for an editable certificate titled '{title}'. Focus on important digital template.  Provide only one paragraph without extra suggestions.",
        "alt_fourth": f"Create one professional Alt text (300–450 characters) for an editable and printable certificate titled '{title}'. Focus on describing style, usability, and ideal customer.  Provide only one paragraph without extra suggestions."
    }

    # Call Gemini for each prompt
    generated = {}
    for key, prompt in prompts.items():
        result = await call_gemini(prompt)
        generated[key] = result if result else "Content unavailable."

    # Clean and trim
    generated["etsy_title"] = generated["etsy_title"][:140]
    generated["alt_primary"] = generated["alt_primary"][:500]
    generated["alt_secondary"] = generated["alt_secondary"][:500]
    generated["alt_third"] = generated["alt_third"][:500]
    generated["alt_fourth"] = generated["alt_fourth"][:500]

    return generated
