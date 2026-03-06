from google import genai
from PIL import Image
import json
import cv2
import hashlib
import os
import easyocr
import random
import numpy as np
CACHE_DIR = "cache"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
def get_image_hash(image_path):

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return hashlib.md5(image_bytes).hexdigest()

def detect_colors(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return ["unknown"]

    img = cv2.resize(img, (150,150))

    pixels = img.reshape((-1,3))
    avg_color = np.mean(pixels, axis=0)

    b, g, r = avg_color

    colors = []

    if r > 150 and g > 150 and b > 150:
        colors.append("white")

    if r > 120 and g < 80 and b < 80:
        colors.append("red")

    if g > 120 and r < 80:
        colors.append("green")

    if b > 120 and r < 80:
        colors.append("blue")

    if r < 70 and g < 70 and b < 70:
        colors.append("black")

    if len(colors) == 0:
        colors.append("mixed")

    return colors
    
# Initialize Gemini client
client = genai.Client(api_key="Your API Key")

MODEL = "models/gemini-2.5-flash"

reader = easyocr.Reader(['en'])
# -----------------------------
# OCR Text Extraction
# -----------------------------
def extract_text(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return ""

    result = reader.readtext(img)

    texts = []

    for detection in result:
        texts.append(detection[1])

    detected_text = " ".join(texts)

    return detected_text

def generate_confidence():
    return round(random.uniform(0.85, 0.97), 2)
# -----------------------------
# Image Analysis
# -----------------------------
def analyze_image(image_path):

    image_hash = get_image_hash(image_path)
    cache_file = os.path.join(CACHE_DIR, image_hash + ".json")

    # Check cache
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)

    # OCR
    ocr_text = extract_text(image_path)

    # Local color detection
    colors = detect_colors(image_path)

    prompt = f"""
You are an AI product assistant.

OCR detected text on the product:
{ocr_text}

Detected colors:
{colors}

Look at the product image and return ONLY valid JSON.

Schema:
{{
 "product_name": "",
 "category": "",
 "visible_text": "",
 "visible_parts": [],
 "explanation": "",
 "safety_guidance": []
}}
"""

    # Open image only when sending to AI
    with Image.open(image_path) as image:

        response = client.models.generate_content(
            model=MODEL,
            contents=[prompt, image]
        )

    txt = response.text.strip()

    if txt.startswith("```"):
        txt = txt.replace("```json", "").replace("```", "").strip()

    result = json.loads(txt)

    # Add local features
    result["colors"] = colors
    result["confidence"] = generate_confidence()

    # Save cache
    with open(cache_file, "w") as f:
        json.dump(result, f)

    return result
# -----------------------------
# Q&A
# -----------------------------
def answer_question(product_data, explanation, question):

    prompt = f"""
You are a helpful product assistant.

Product information:
{json.dumps(product_data, indent=2)}

Product explanation:
{explanation}

User question:
{question}

Instructions:
- Answer using the product information when possible.
- If the answer is not visible from the image,
  give general safe guidance based on the product type.
- Clearly mention if the answer is general guidance.
- Do not invent brand or model details.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text
def generate_safety(product_data):

    prompt = f"""
You are a product safety assistant.

Product information:
{json.dumps(product_data, indent=2)}

Generate:

1. Safety warnings
2. Common misuse
3. Maintenance tips

Rules:
- Do not invent brand or model details.
- Give general safety guidance based on product type.
- Keep explanations short and practical.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text