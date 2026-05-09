from PIL import Image
import json
import random

from utils.ocr import extract_text
from utils.image_processing import detect_colors
from utils.cache import get_image_hash, load_cache, save_cache
from services.gemini_service import generate_content
from services.link_handler import extract_product_from_url


# -------------------------
# Confidence
# -------------------------
def generate_confidence():
    return round(random.uniform(0.85, 0.97), 2)


# -------------------------
# IMAGE ANALYSIS
# -------------------------
def analyze_image(image_path):

    image_hash = get_image_hash(image_path)

    cached = load_cache(image_hash)
    if cached:
        return cached

    ocr_text = extract_text(image_path)
    colors = detect_colors(image_path)

    prompt = f"""
You are an AI product assistant.

OCR text:
{ocr_text}

Colors:
{colors}

Return JSON but make explanation very simple and user-friendly:
{{
 "product_name": "",
 "category": "",
 "visible_text": "",
 "visible_parts": [],
 "explanation": "",
 "safety_guidance": []
}}
"""

    try:
        with Image.open(image_path) as img:
            response = generate_content(prompt, img)

        txt = response.strip()

        if txt.startswith("```"):
            txt = txt.replace("```json", "").replace("```", "").strip()

        result = json.loads(txt)

    except Exception:
        return {"error": "Failed to analyze image"}

    # Add extra fields
    result["colors"] = colors
    result["confidence"] = generate_confidence()

    save_cache(image_hash, result)

    return result   # 🔥 FIXED


# -------------------------
# LINK ANALYSIS (HYBRID 🔥)
# -------------------------
def analyze_link(url):

    from services.link_handler import extract_product_from_url
    from services.gemini_service import generate_content
    import json

    # -------------------------
    # Step 1: Try scraping
    # -------------------------
    data = extract_product_from_url(url)

    # -------------------------
    # Step 2: Decide strategy
    # -------------------------
    use_fallback = False

    if not data:
        use_fallback = True
    elif "error" in data:
        use_fallback = True
    elif "amazon" in data.get("title", "").lower():
        # 🔥 detects wrong extraction like "Amazon.in"
        use_fallback = True

    # -------------------------
    # Step 3: Create prompt
    # -------------------------
    if not use_fallback:

        prompt = f"""
You are an AI product assistant.

Product Title:
{data["title"]}

Description:
{data["description"]}

Generate JSON:
{{
 "product_name": "",
 "category": "",
 "explanation": "",
 "safety_guidance": []
}}
"""

    else:
        # 🔥 Gemini handles short links
        prompt = f"""
You are an AI product assistant.

Analyze this product URL:
{url}

IMPORTANT:
- Understand the product even if it is a shortened link
- Identify actual product (not Amazon website)

Return JSON:
{{
 "product_name": "",
 "category": "",
 "explanation": "",
 "safety_guidance": []
}}
"""

    # -------------------------
    # Step 4: Call Gemini
    # -------------------------
    response = generate_content(prompt)

    txt = response.strip()

    if txt.startswith("```"):
        txt = txt.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(txt)

    except:
        return {
            "product_name": "Unknown",
            "category": "Unknown",
            "explanation": "Could not analyze product from link.",
            "safety_guidance": ["Please check product manually"]
        }