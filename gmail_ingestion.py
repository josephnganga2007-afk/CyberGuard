from email_pipeline import process_email

from database import (
    gmail_message_exists,
    investigation_exists,
    save_transaction,
    save_investigation,
    get_business_by_gmail_account,
    get_business_by_id,
)


def ingest_email(email, business_id=None):

    # ---------------------------------------------------------
    # GMAIL MESSAGE ID
    # ---------------------------------------------------------

    mid = (
        email.get("gmail_message_id")
        or email.get("message_id")
        or email.get("id")
    )

    if not mid:
        return {
            "status": "ERROR",
            "reason": "Missing Gmail message ID."
        }

    # ---------------------------------------------------------
    # BUSINESS RESOLUTION
    # ---------------------------------------------------------

    if business_id is not None:
        business = get_business_by_id(business_id)

    else:
        business = get_business_by_gmail_account(
            email.get("gmail_account")
        )

        if business:
            business_id = business["id"]

    if not business:
        return {
            "status": "ERROR",
            "reason": "Could not resolve a business for this email."
        }

    # ---------------------------------------------------------
    # BUSINESS-SCOPED DUPLICATE PROTECTION
    # ---------------------------------------------------------

    if (
        gmail_message_exists(mid, business_id)
        or investigation_exists(mid, business_id)
    ):
        return {
            "status": "DUPLICATE",
            "gmail_message_id": mid,
            "business_id": business_id,
        }

    # ---------------------------------------------------------
    # EMAIL PIPELINE
    # ---------------------------------------------------------

    result = process_email(
        email,
        business_id=business_id
    )

    if not result:
        return {
            "status": "ERROR",
            "reason": "Email processing returned no result."
        }

    action = result.get("action")
    category = result.get("category")

    # ---------------------------------------------------------
    # TRIAGE DATA
    # ---------------------------------------------------------

    triage = result.get("triage") or {}

    triage_reason = (
        triage.get("reason")
        or result.get("reason")
    )

    triage_signals = (
        triage.get("signals")
        or result.get("signals")
        or []
    )

    # ---------------------------------------------------------
    # IRRELEVANT EMAIL
    # ---------------------------------------------------------

    if action == "STOP" or category == "IRRELEVANT":
        return {
            "status": "SKIPPED",
            "category": category,
            "action": action,
            "reason": triage_reason,
            "gmail_message_id": mid,
            "business_id": business_id,
        }

    # ---------------------------------------------------------
    # COMMON EMAIL DATA
    # ---------------------------------------------------------

    supplier = result.get("supplier") or {}

    name = (
        supplier.get("name")
        or result.get("supplier_name")
        or "Unknown Supplier"
    )

    sender = (
        result.get("sender")
        or email.get("sender")
        or email.get("from")
        or ""
    )

    subject = (
        result.get("subject")
        or email.get("subject")
        or ""
    )

    message = (
        result.get("message")
        or email.get("body")
        or email.get("message")
        or ""
    )

    # ---------------------------------------------------------
    # RISK DATA
    #
    # email_pipeline stores PAYMENT_RELATED analysis inside:
    #
    # result["risk"]["score"]
    # result["risk"]["risk_level"]
    # result["risk"]["requested_account"]
    #
    # Keep top-level fallbacks for compatibility.
    # ---------------------------------------------------------

    risk = result.get("risk") or {}

    account = (
        risk.get("requested_account")
        if risk.get("requested_account") is not None
        else result.get("requested_account")
    )

    score = risk.get(
        "score",
        result.get("risk_score", 0)
    )

    level = risk.get(
        "risk_level",
        result.get("risk_level", "LOW")
    )

    if score is None:
        score = 0

    if level is None:
        level = "LOW"

    # ---------------------------------------------------------
    # UNCERTAIN -> HUMAN INVESTIGATION
    # ---------------------------------------------------------

    if (
        category == "UNCERTAIN"
        or action == "HOLD_FOR_REVIEW"
    ):

        investigation_id = save_investigation(
            name,
            sender,
            subject,
            message,
            account,
            score,
            level,
            business_id=business_id,
            gmail_message_id=mid,
            triage_reason=triage_reason,
            triage_signals=triage_signals,
        )

        return {
            "status": "PROCESSED",
            "type": "INVESTIGATION",
            "investigation_id": investigation_id,
            "category": category,
            "action": action,
            "reason": triage_reason,
            "gmail_message_id": mid,
            "business_id": business_id,
        }

    # ---------------------------------------------------------
    # PAYMENT RELATED -> TRANSACTION
    # ---------------------------------------------------------

    transaction_id = save_transaction(
        name,
        message,
        score,
        level,
        account,
        "GMAIL",
        mid,
        business_id,
    )

    return {
        "status": "PROCESSED",
        "type": "TRANSACTION",
        "transaction_id": transaction_id,
        "category": category,
        "action": action,
        "reason": triage_reason,
        "risk_score": score,
        "risk_level": level,
        "requested_account": account,
        "gmail_message_id": mid,
        "business_id": business_id,
    }