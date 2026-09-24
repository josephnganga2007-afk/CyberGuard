from triage_engine import triage_email
from risk_engine import analyze_transaction


def build_risk_message(email):
    """
    Convert a structured email into the message format
    expected by the existing risk engine.
    """

    return (
        f"From: {email['sender']}\n"
        f"Subject: {email['subject']}\n"
        f"\n"
        f"{email['body']}"
    )


def process_email(email, supplier):
    """
    Run an email through the CyberGuard pipeline.

    Triage happens first.

    IRRELEVANT:
        Stop immediately.

    UNCERTAIN:
        Do not automatically run fraud analysis.

    PAYMENT_RELATED:
        Pass the original email into the deterministic
        risk engine.
    """

    triage_result = triage_email(email)

    category = triage_result["category"]

    # --------------------------------------------------
    # IRRELEVANT
    # --------------------------------------------------

    if category == "IRRELEVANT":

        return {
            "stage": "TRIAGE",
            "category": "IRRELEVANT",
            "action": "STOP",
            "triage": triage_result,
            "risk": None
        }

    # --------------------------------------------------
    # UNCERTAIN
    # --------------------------------------------------

    if category == "UNCERTAIN":

        return {
            "stage": "TRIAGE",
            "category": "UNCERTAIN",
            "action": "HOLD_FOR_REVIEW",
            "triage": triage_result,
            "risk": None
        }

    # --------------------------------------------------
    # PAYMENT RELATED
    # --------------------------------------------------

    if category == "PAYMENT_RELATED":

        risk_message = build_risk_message(email)

        score, risk_level, warnings, factors = analyze_transaction(
            risk_message,
            supplier
        )

        return {
            "stage": "RISK_ANALYSIS",
            "category": "PAYMENT_RELATED",
            "action": "ANALYZE",
            "triage": triage_result,
            "risk": {
                "score": score,
                "risk_level": risk_level,
                "warnings": warnings,
                "factors": factors
            }
        }

    # --------------------------------------------------
    # Safety fallback
    # --------------------------------------------------

    return {
        "stage": "TRIAGE",
        "category": "UNKNOWN",
        "action": "HOLD_FOR_REVIEW",
        "triage": triage_result,
        "risk": None
    }