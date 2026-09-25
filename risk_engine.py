import re


# ============================================================
# TEXT / EXTRACTION HELPERS
# ============================================================

def extract_email(sender):
    match = re.search(
        r"<([^>]+)>",
        sender
    )

    if match:
        return match.group(1).strip().lower()

    return sender.strip().lower()


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


def _normalise_text(message):
    return " ".join(message.lower().split())


# ============================================================
# NEGATIVE / SAFE CONTEXT
# ============================================================

def has_no_change_context(message):
    text = _normalise_text(message)

    safe_patterns = [
        r"\bremains?\s+unchanged\b",
        r"\bremain\s+unchanged\b",
        r"\bis\s+unchanged\b",
        r"\bare\s+unchanged\b",
        r"\bno\s+changes?\s+(?:are\s+)?required\b",
        r"\bno\s+change\b",
        r"\bwithout\s+(?:any\s+)?changes?\b",
        r"\bcontinue\s+(?:to\s+)?use\b.*\bexisting\b",
        r"\bcontinue\s+using\b.*\bexisting\b",
        r"\bexisting\s+payment\s+(?:account|destination)\b"
    ]

    return any(
        re.search(pattern, text)
        for pattern in safe_patterns
    )


# ============================================================
# BENEFICIARY / PAYMENT DESTINATION CHANGE
# ============================================================

def has_beneficiary_change(message):
    """
    Detect a meaningful change in where money should be sent.

    Important:
    - Generic account language alone is deliberately NOT enough.
    - Payment/banking/receiving context is required for ambiguous
      phrases such as "new account".
    - Explicit safe/unchanged language suppresses destination
      change detection.
    """

    text = _normalise_text(message)

    if has_no_change_context(text):
        return False

    # --------------------------------------------------------
    # Explicit beneficiary changes
    # --------------------------------------------------------

    beneficiary_patterns = [
        r"\b(?:changed?|change|changing|updated?|update|revised|replace|replacement)\b"
        r".{0,40}\bbeneficiary\b",

        r"\bbeneficiary\b"
        r".{0,40}\b(?:changed?|change|changing|updated?|update|revised|new)\b"
    ]

    if any(
        re.search(pattern, text)
        for pattern in beneficiary_patterns
    ):
        return True

    # --------------------------------------------------------
    # Explicit payment destination changes
    # --------------------------------------------------------

    destination_patterns = [
        r"\bpayment\s+destination\b"
        r".{0,40}\b(?:changed?|change|updated?|update|revised|new)\b",

        r"\b(?:changed?|change|updated?|update|revised|amend|amended|new)\b"
        r".{0,40}\bpayment\s+destination\b",

        r"\breceiving\s+account\b"
        r".{0,40}\b(?:changed?|change|updated?|update|revised|new)\b",

        r"\b(?:changed?|change|updated?|update|revised|new)\b"
        r".{0,40}\breceiving\s+account\b",

        r"\breceiving\s+details\b"
        r".{0,40}\b(?:changed?|change|updated?|update|revised|new)\b",

        r"\b(?:changed?|change|updated?|update|revised|new)\b"
        r".{0,40}\breceiving\s+details\b",

        r"\bbank\s+account\b"
        r".{0,40}\b(?:changed?|change|updated?|update|revised|new)\b",

        r"\b(?:changed?|change|updated?|update|revised|new)\b"
        r".{0,40}\bbank\s+account\b",

        r"\bbanking\s+details\b"
        r".{0,40}\b(?:changed?|change|updated?|update|revised|new)\b",

        r"\b(?:changed?|change|updated?|update|revised|new)\b"
        r".{0,40}\bbanking\s+details\b"
    ]

    if any(
        re.search(pattern, text)
        for pattern in destination_patterns
    ):
        return True

    # --------------------------------------------------------
    # Payment directed to a new/revised account
    #
    # "Please use the new account." -> False
    # "Send the payment to the new account." -> True
    # --------------------------------------------------------

    payment_to_new_account_patterns = [
        r"\b(?:payment|funds|balance|invoice|remittance|transfer)\b"
        r".{0,50}\b(?:to|into|using)\b"
        r".{0,30}\b(?:new|revised|updated)\s+account\b",

        r"\b(?:send|pay|transfer|route|redirect)\b"
        r".{0,50}\b(?:payment|funds|balance|invoice|remittance)\b"
        r".{0,50}\b(?:new|revised|updated)\s+account\b"
    ]

    if any(
        re.search(pattern, text)
        for pattern in payment_to_new_account_patterns
    ):
        return True

    # --------------------------------------------------------
    # Explicit redirection / rerouting of money
    # --------------------------------------------------------

    redirect_patterns = [
        r"\bredirect\b.{0,60}\b(?:payment|funds|balance|invoice|transfer)\b",
        r"\bredirect\b.{0,80}\b(?:receiving|banking|account|destination|details)\b",

        r"\broute\b.{0,60}\b(?:payment|funds|balance|invoice|remittance|transfer)\b",
        r"\broute\b.{0,80}\b(?:revised|new|updated)\b.{0,30}"
        r"\b(?:account|recipient|destination|details)\b",

        r"\b(?:payment|funds|balance|invoice|remittance|transfer)\b"
        r".{0,60}\bredirect\b",

        r"\b(?:payment|funds|balance|invoice|remittance|transfer)\b"
        r".{0,60}\broute\b"
    ]

    if any(
        re.search(pattern, text)
        for pattern in redirect_patterns
    ):
        return True

    # --------------------------------------------------------
    # "Route the next payment using the details below"
    # --------------------------------------------------------

    route_payment_details_patterns = [
        r"\b(?:route|redirect|send)\b"
        r".{0,50}\b(?:payment|funds|balance|remittance|transfer)\b"
        r".{0,50}\b(?:details|destination|account|recipient)\b",

        r"\b(?:payment|funds|balance|remittance|transfer)\b"
        r".{0,50}\b(?:using|to)\b"
        r".{0,30}\b(?:details\s+below|new\s+details|revised\s+details)\b"
    ]

    if any(
        re.search(pattern, text)
        for pattern in route_payment_details_patterns
    ):
        return True

    # --------------------------------------------------------
    # New remittance destination
    # --------------------------------------------------------

    remittance_patterns = [
        r"\bremittances?\b"
        r".{0,60}\b(?:new|revised|updated)\s+destination\b",

        r"\b(?:new|revised|updated)\s+remittance\s+destination\b"
    ]

    if any(
        re.search(pattern, text)
        for pattern in remittance_patterns
    ):
        return True

    # --------------------------------------------------------
    # Replacement of account used specifically for payment
    # --------------------------------------------------------

    replacement_patterns = [
        r"\breplace\b"
        r".{0,40}\baccount\b"
        r".{0,40}\b(?:payment|payments|paying)\b",

        r"\baccount\b"
        r".{0,40}\b(?:used|use)\b"
        r".{0,30}\b(?:for|to)\s+payments?\b"
        r".{0,30}\b(?:replace|replacement|new)\b"
    ]

    if any(
        re.search(pattern, text)
        for pattern in replacement_patterns
    ):
        return True

    return False


# ============================================================
# BANKING DETAILS CHANGE
# ============================================================

def has_banking_change(message):
    text = _normalise_text(message)

    if has_no_change_context(text):
        return False

    patterns = [
        r"\bchanged?\s+our\s+banking\b",
        r"\bchanged?\s+our\s+bank\b",
        r"\bchanged?\s+bank\s+details\b",
        r"\bchanged?\s+banking\s+details\b",
        r"\bupdated?\s+banking\s+details\b",
        r"\bupdated?\s+bank\s+details\b",
        r"\bnew\s+bank\s+account\b",
        r"\bchange\s+bank\s+account\b",
        r"\bchange\s+banking\s+details\b",
        r"\bchange\s+bank\s+details\b",
        r"\bnew\s+banking\s+details\b",

        r"\bbank\s+account\s+has\s+changed\b",
        r"\bbank\s+account\s+changed\b",

        r"\breceiving\s+account\s+has\s+changed\b",
        r"\breceiving\s+account\s+changed\b",

        r"\breceiving\s+details\s+have\s+been\s+updated\b",
        r"\breceiving\s+details\s+updated\b",

        r"\bpayment\s+destination\s+has\s+changed\b",
        r"\bpayment\s+destination\s+changed\b"
    ]

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


# ============================================================
# MAIN DETERMINISTIC ENGINE
# ============================================================

def analyze_transaction(message, supplier):

    message_lower = message.lower()

    score = 0
    warnings = []
    factors = []

    # --------------------------------------------------------
    # EXTRACT SENDER
    # --------------------------------------------------------

    sender_match = re.search(
        r"from:\s*(?:.*?<)?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})(?:>)?",
        message,
        re.IGNORECASE
    )

    sender_email = (
        sender_match.group(1).lower()
        if sender_match
        else ""
    )

    requested_account = extract_requested_account(
        message
    )

    trusted_email = (
        supplier.get("email", "").strip().lower()
    )

    trusted_account = str(
        supplier.get("account_last_four", "")
    ).strip()

    # --------------------------------------------------------
    # SUPPLIER / ACCOUNT VERIFICATION
    # --------------------------------------------------------

    sender_match_result = None
    account_match_result = None

    if trusted_email:
        sender_match_result = (
            sender_email == trusted_email
        )

    if trusted_account and requested_account:
        account_match_result = (
            requested_account == trusted_account
        )

    print(
        f"DEBUG SENDER: '{sender_email}'"
    )

    print(
        f"DEBUG TRUSTED: '{trusted_email}'"
    )

    print(
        f"DEBUG MATCH: {sender_match_result}"
    )

    print(
        f"DEBUG REQUESTED ACCOUNT: "
        f"'{requested_account}'"
    )

    print(
        f"DEBUG TRUSTED ACCOUNT: "
        f"'{trusted_account}'"
    )

    print(
        f"DEBUG ACCOUNT MATCH: "
        f"{account_match_result}"
    )

    # --------------------------------------------------------
    # CONTEXT DETECTION
    # --------------------------------------------------------

    banking_change = has_banking_change(
        message
    )

    destination_change = has_beneficiary_change(
        message
    )

    # --------------------------------------------------------
    # BANKING DETAILS
    # --------------------------------------------------------

    banking_reference_signals = [
        "banking details",
        "bank details",
        "bank account",
        "account number",
        "banking information"
    ]

    if banking_change:

        score += 30

        warnings.append(
            "Banking details change detected"
        )

        factors.append({
            "name": "Banking details change",
            "score": 30,
            "points": 30
        })

    elif any(
        signal in message_lower
        for signal in banking_reference_signals
    ):

        warnings.append(
            "Banking details referenced"
        )

    # --------------------------------------------------------
    # URGENCY
    # --------------------------------------------------------

    urgency_signals = [
        "urgent",
        "urgently",
        "immediately",
        "as soon as possible",
        "right away",
        "immediate action",
        "action required"
    ]

    urgency_detected = any(
        signal in message_lower
        for signal in urgency_signals
    )

    if urgency_detected:

        score += 15

        warnings.append(
            "Urgent payment request detected"
        )

        factors.append({
            "name": "Urgency",
            "score": 15,
            "points": 15
        })

    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    payment_signals = [
        "pay",
        "payment",
        "make payment",
        "pay invoice",
        "settle invoice",
        "transfer",
        "send payment",
        "remittance",
        "remittances",
        "outstanding balance"
    ]

    payment_detected = any(
        signal in message_lower
        for signal in payment_signals
    )

    if payment_detected:

        score += 15

        factors.append({
            "name": "Payment-related request",
            "score": 15,
            "points": 15
        })

    # --------------------------------------------------------
    # BENEFICIARY CHANGE
    #
    # Keep the historical factor name for explicit beneficiary
    # language because regression tests recognise both factor
    # names as destination changes.
    # --------------------------------------------------------

    beneficiary_word_present = (
        "beneficiary" in message_lower
    )

    if destination_change and beneficiary_word_present:

        score += 10

        factors.append({
            "name": "Beneficiary change",
            "score": 10,
            "points": 10
        })

    # --------------------------------------------------------
    # PAYMENT DESTINATION CHANGE
    #
    # Do not double-score explicit beneficiary language as both
    # beneficiary + destination. Other destination changes get
    # this factor.
    # --------------------------------------------------------

    if destination_change and not beneficiary_word_present:

        score += 10

        warnings.append(
            "Payment destination may have changed"
        )

        factors.append({
            "name": "Payment destination change",
            "score": 10,
            "points": 10
        })

    elif destination_change and beneficiary_word_present:

        # Historical behavior for genuine beneficiary changes
        # included the destination-change factor as well.
        score += 10

        warnings.append(
            "Payment destination may have changed"
        )

        factors.append({
            "name": "Payment destination change",
            "score": 10,
            "points": 10
        })

    # --------------------------------------------------------
    # URGENT DESTINATION CHANGE
    # --------------------------------------------------------

    if urgency_detected and destination_change:

        score += 10

        factors.append({
            "name": "Urgent destination change",
            "score": 10,
            "points": 10
        })

    # --------------------------------------------------------
    # SUPPLIER EMAIL MISMATCH
    # --------------------------------------------------------

    if sender_match_result is False:

        score += 20

        warnings.append(
            "Sender does not match trusted supplier email"
        )

        factors.append({
            "name": "Supplier email mismatch",
            "score": 20,
            "points": 20
        })

    # --------------------------------------------------------
    # ACCOUNT MISMATCH
    # --------------------------------------------------------

    if account_match_result is False:

        score += 25

        warnings.append(
            f"Requested account ending "
            f"{requested_account} "
            f"does not match trusted supplier account"
        )

        factors.append({
            "name": "Account mismatch",
            "score": 25,
            "points": 25
        })

    # --------------------------------------------------------
    # UNKNOWN SUPPLIER DIAGNOSTIC
    # --------------------------------------------------------

    if not trusted_email:

        warnings.append(
            "No trusted supplier email available for verification"
        )

    # --------------------------------------------------------
    # CAP
    # --------------------------------------------------------

    score = min(
        score,
        100
    )

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if score >= 80:
        risk_level = "CRITICAL"

    elif score >= 60:
        risk_level = "HIGH"

    elif score >= 30:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    message_score = 0
    supplier_score = 0

    for factor in factors:

        if factor["name"] in [
            "Supplier email mismatch",
            "Account mismatch"
        ]:

            supplier_score += factor["points"]

        else:

            message_score += factor["points"]

    print("=" * 60)

    print(
        "CYBERGUARD DETERMINISTIC ANALYSIS"
    )

    print(
        f"MESSAGE SCORE: {message_score}"
    )

    print(
        f"SUPPLIER SCORE: {supplier_score}"
    )

    print(
        f"FINAL SCORE: {score}"
    )

    print(
        f"RISK LEVEL: {risk_level}"
    )

    print(
        f"WARNINGS: {warnings}"
    )

    print(
        f"FACTORS: {factors}"
    )

    print(
        f"REQUESTED ACCOUNT: "
        f"{requested_account}"
    )

    print("=" * 60)

    return (
        score,
        risk_level,
        warnings,
        factors
    )