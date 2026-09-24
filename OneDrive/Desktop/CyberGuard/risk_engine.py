import re


def analyze_message(message):
    message = message.lower()

    score = 0
    warnings = []
    factors = []

    if "banking details" in message or "bank details" in message:
        score += 30
        warning = "Request to change banking details detected"

        warnings.append(warning)
        factors.append({
            "name": "Banking details change",
            "points": 30
        })

    if (
        "urgent" in message
        or "immediately" in message
        or "today" in message
        or "as soon as possible" in message
    ):
        score += 15
        warning = "Urgency language detected"

        warnings.append(warning)
        factors.append({
            "name": "Urgency language",
            "points": 15
        })

    if (
        "payment" in message
        or "pay" in message
        or "invoice" in message
    ):
        score += 15
        warning = "Payment-related request detected"

        warnings.append(warning)
        factors.append({
            "name": "Payment-related request",
            "points": 15
        })

    return score, warnings, factors


def check_supplier(message, supplier):

    warnings = []
    factors = []
    score = 0

    message_lower = message.lower()

    # Email verification
    if supplier["email"].lower() not in message_lower:

        score += 20

        warning = "Sender does not match trusted supplier email"

        warnings.append(warning)

        factors.append({
            "name": "Supplier email mismatch",
            "points": 20
        })

    # Account number detection
    account_match = re.search(
        r"(?:account|account number|a/c)\s*(?:is|:)?\s*(\d{4,})",
        message_lower
    )

    if account_match:

        mentioned_account = account_match.group(1)

        if mentioned_account[-4:] != supplier["account_last_four"]:

            score += 25

            warning = "Bank account does not match trusted supplier record"

            warnings.append(warning)

            factors.append({
                "name": "Bank account mismatch",
                "points": 25
            })

        else:

            warnings.append(
                "Bank account matches trusted supplier record"
            )

    elif (
        "banking details" in message_lower
        or "bank details" in message_lower
    ):

        score += 20

        warning = (
            "Banking details mentioned but no account number was provided"
        )

        warnings.append(warning)

        factors.append({
            "name": "Unverified banking change",
            "points": 20
        })

    return score, warnings, factors


def analyze_transaction(message, supplier):

    message_score, message_warnings, message_factors = analyze_message(
        message
    )

    supplier_score, supplier_warnings, supplier_factors = check_supplier(
        message,
        supplier
    )

    total_score = min(
        message_score + supplier_score,
        100
    )

    warnings = message_warnings + supplier_warnings

    factors = message_factors + supplier_factors

    if total_score >= 80:
        risk_level = "CRITICAL"

    elif total_score >= 60:
        risk_level = "HIGH"

    elif total_score >= 30:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return total_score, risk_level, warnings, factors