import json
from services.gemini_service import generate_content

def generate_safety(product_data):

    prompt = f"""
Product:
{json.dumps(product_data, indent=2)}

Generate:
- Safety warnings
- Misuse
- Maintenance
"""

    return generate_content(prompt)