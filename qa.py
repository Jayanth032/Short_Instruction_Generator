import json
from services.gemini_service import generate_content

def answer_question(product_data, explanation, question):

    prompt = f"""
Product:
{json.dumps(product_data, indent=2)}

Explanation:
{explanation}

Question:
{question}

Rules:
- Use available data
- Otherwise give general guidance
"""

    return generate_content(prompt)