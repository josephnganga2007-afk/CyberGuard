
import re

from triage_engine import triage_email
from risk_engine import analyze_transaction

from database import (
    get_supplier_by_email,
    get_supplier_for_business
)


def build_risk_message(email):

    return (
        f"From: {email['sender']}\n"
        f"Subject: {email['subject']}\n"
        f"\n"
        f"{email['body']}"
    )


def extract_sender_email(sender):

    if "<" in sender and ">" in sender:
        return sender.split("<")[1].split(">")[0].strip()

    return sender.strip()


def extract_requested_account(message):

    patterns = [
        r"account\s*(?:number)?\s*:\s*(\d{4,})",
        r"account\s*(?:number)?\s+is\s+(\d{4,})",
        r"account\s*(?:number)?\s+(\d{4,})",
        r"a/c\s*(?:number)?\s*:\s*(\d{4,})",
        r"a/c\s*(?:number)?\s+(\d{4,})"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message.lower()
        )

        if match:
            return match.group(1)[-4:]

    return None


def process_email(email, business_id=None):

    gmail_message_id = email.get("message_id")

    # ---------------------------------------------------------
    # TRIAGE
    # ---------------------------------------------------------

    triage_result = triage_email(email)

    category = triage_result["category"]

    # ---------------------------------------------------------
    # IRRELEVANT
    # ---------------------------------------------------------

    if category == "IRRELEVANT":

        return {
            "stage": "TRIAGE",
            "category": "IRRELEVANT",
            "action": "STOP",
            "triage": triage_result,
            "risk": None,
            "supplier": None,
            "gmail_message_id": gmail_message_id
        }

    # ---------------------------------------------------------
    # UNCERTAIN
    # ---------------------------------------------------------

    if category == "UNCERTAIN":

        return {
            "stage": "TRIAGE",
            "category": "UNCERTAIN",
            "action": "HOLD_FOR_REVIEW",
            "triage": triage_result,
            "risk": None,
            "supplier": None,
            "gmail_message_id": gmail_message_id
        }

    # ---------------------------------------------------------
    # PAYMENT RELATED
    # ---------------------------------------------------------

    sender_email = extract_sender_email(
        email["sender"]
    )

    # ---------------------------------------------------------
    # BUSINESS-AWARE SUPPLIER RESOLUTION
    # ---------------------------------------------------------

    if business_id is not None:

        supplier = get_supplier_for_business(
            business_id,
            sender_email
        )

    else:

        # Preserve existing V12.7.3 behavior
        supplier = get_supplier_by_email(
            sender_email
        )

    if category == "PAYMENT_RELATED":

        risk_message = build_risk_message(
            email
        )

        # -----------------------------------------------------
        # KNOWN SUPPLIER
        # -----------------------------------------------------

        if supplier:

            score, risk_level, warnings, factors = (
                analyze_transaction(
                    risk_message,
                    supplier
                )
            )

        # -----------------------------------------------------
        # UNKNOWN SUPPLIER
        # -----------------------------------------------------

        else:

            score, risk_level, warnings, factors = (
                analyze_transaction(
                    risk_message,
                    {
                        "name": "UNKNOWN SENDER",
                        "email": "",
                        "account_last_four": ""
                    }
                )
            )

            warnings.insert(
                0,
                "Sender does not match a known supplier for this business."
            )

        # -----------------------------------------------------
        # REQUESTED ACCOUNT
        # -----------------------------------------------------

        requested_account = extract_requested_account(
            risk_message
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
                "factors": factors,
                "requested_account": requested_account
            },
            "supplier": supplier,
            "business_id": business_id,
            "gmail_message_id": gmail_message_id
        }

    # ---------------------------------------------------------
    # SAFETY FALLBACK
    # ---------------------------------------------------------

    return {
        "stage": "TRIAGE",
        "category": "UNKNOWN",
        "action": "HOLD_FOR_REVIEW",
        "triage": triage_result,
        "risk": None,
        "supplier": None,
        "business_id": business_id,
        "gmail_message_id": gmail_message_id
    }

