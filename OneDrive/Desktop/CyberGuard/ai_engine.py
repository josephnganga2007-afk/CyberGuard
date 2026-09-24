import os
from google import genai
from pydantic import BaseModel


# ==========================================
# Gemini structured response
# ==========================================

class CyberGuardAIResult(BaseModel):
    assessment: str
    confidence: str
    threat_type: str
    indicators: list[str]


# ==========================================
# Gemini client
# ==========================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set."
    )

client = genai.Client(api_key=api_key)


# ==========================================
# AI analysis
# ==========================================

def analyze_with_ai(message):

    prompt = f"""
You are the AI analysis engine for CyberGuard,
a payment fraud detection system.

Analyze the following payment-related communication.

Your job is to identify signs of:
- payment diversion
- social engineering
- suspicious banking changes
- urgency or pressure
- impersonation
- unusual payment instructions
- attempts to bypass normal verification
- other characteristics associated with business email compromise

Do NOT make up facts that are not present in the message.

Return a concise assessment.

Payment communication:
Classify the most likely threat type.

Examples:
- Business Email Compromise (BEC)
- Payment Diversion
- Phishing
- Social Engineering
- Suspicious Banking Change
- No Significant Threat

If there is insufficient evidence, use "Unclassified".
{message}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",

            contents=prompt,

            config={
                "response_mime_type": "application/json",
                "response_schema": CyberGuardAIResult,
            }
        )

        result = response.parsed

        if result is None:
            raise ValueError("Gemini returned no structured result.")

        return {
            "assessment": result.assessment,
            "confidence": result.confidence,
            "threat_type": result.threat_type,
            "indicators": result.indicators
        }

    except Exception as e:

        print("Gemini AI error:", e)

        return {
    "assessment": "AI analysis unavailable.",
    "confidence": "UNAVAILABLE",
    "threat_type": "UNAVAILABLE",
    "indicators": [
        "Gemini analysis could not be completed."
    ]
}
    