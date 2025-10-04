from fastapi import APIRouter
from ..schemas.contracts import PSParseIn, PSParseOut, PSGenIn, PSGenOut
from ..utils.log import logger
import google.generativeai as genai
import json
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

router = APIRouter(prefix="/ps", tags=["problem-statement"])

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")


@router.post("/parse", response_model=PSParseOut)
def parse_ps(body: PSParseIn):
    prompt = f"""
    You are an AI that extracts problem statements into structured form.
    Problem: {body.text}

    Extract:
    - task_type (classification/regression/etc.)
    - domain (finance/healthcare/etc.)
    - target (prediction target)
    - entities
    - keywords
    - constraints
    - plan (steps to solve)

    Respond ONLY in valid JSON.
    """

    logger.info("📌 Sending problem statement to Gemini")

    resp = model.generate_content(prompt)

    try:
        parsed = json.loads(resp.text)   # ✅ parse JSON
        return PSParseOut(**parsed)      # ✅ validate with Pydantic
    except Exception as e:
        logger.error(f"❌ Failed to parse Gemini response: {e}")
        return PSParseOut(
            task_type="classification",
            domain="unknown",
            target="unknown",
            entities=[],
            keywords=body.text.split(),
            constraints={},
            plan={}
        )


@router.post("/generate", response_model=PSGenOut)
def generate_ps(body: PSGenIn):
    prompt = f"""
    You are an AI assistant that generates problem statements.

    Domain: {body.domain}
    Goal: {body.goal}
    Constraints: {body.constraints}

    Generate 3 alternative problem statements as JSON:
    - title
    - statement
    - task_type
    - metrics
    """

    resp = model.generate_content(prompt)

    try:
        parsed = json.loads(resp.text)
        return PSGenOut(**parsed)
    except Exception as e:
        logger.error(f"❌ Failed to parse Gemini response: {e}")
        return PSGenOut(options=[])
