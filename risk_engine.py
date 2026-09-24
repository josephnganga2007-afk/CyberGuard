import re


# ============================================================
# CYBERGUARD DETERMINISTIC RISK ENGINE
# ============================================================

BANKING_TERMS = (
    "banking details",
    "bank details",
    "bank account",
    "account details",
)

URGENCY_TERMS = (
    "urgent",
    "immediately",
    "as soon as possible",
    "asap",
    "right away",
    "without delay",
    "act now",
    "action required immediately",
)

PAYMENT_TERMS = (
    "payment",
    "pay",
    "transfer",
    "wire transfer",
    "send funds",
    "send money",
    "eft",
    "settle",
    "remittance",
    "remit",
    "funds",
)

FINANCIAL_OBLIGATION_TERMS = (
    "outstanding balance",
    "outstanding amount",
    "amount due",
    "balance due",
    "amount owing",
    "money owed",
    "invoice due",
    "invoice is due",
    "payment terms",
    "normal payment terms",
)

BENEFICIARY_CHANGE_TERMS = (
    "new beneficiary",
    "new beneficiary details",
    "updated beneficiary",
    "updated beneficiary details",
    "changed beneficiary",
    "changed beneficiary details",
    "changed our beneficiary",
    "changed our beneficiary details",
    "change beneficiary",
    "change the beneficiary",
    "change our beneficiary",
    "change your beneficiary",
    "update beneficiary",
    "update the beneficiary",
    "update our beneficiary",
    "update your beneficiary",
    "beneficiary details have changed",
    "beneficiary details changed",
    "different beneficiary",
    "replace beneficiary",
    "replace the beneficiary",
)

DESTINATION_CHANGE_TERMS = (
    "new",
    "updated",
    "update",
    "change",
    "changed",
    "different",
    "amend",
    "amended",
    "replace",
    "replaced",
    "replacement",
    "revised",
    "revise",
    "redirect",
    "redirected",
    "redirecting",
    "alternative",
    "altered",
    "alter",
    "latest",
)

REDIRECTION_TERMS = (
    "route",
    "direct",
    "redirect",
    "send",
    "settle",
    "transfer",
    "pay",
)

REDIRECTION_TARGET_TERMS = (
    "account",
    "details",
    "instructions",
    "destination",
    "recipient",
    "beneficiary",
    "route",
)

REDIRECTION_MARKERS = (
    "instead",
    "below",
    "new details",
    "different account",
    "alternative account",
    "alternative route",
    "using the details",
    "using the information",
    "using the instructions",
    "shown in the attachment",
    "listed below",
    "provided below",
    "provided",
)

STABILITY_TERMS = (
    "existing beneficiary",
    "existing payment destination",
    "existing receiving account",
    "existing receiving details",
    "existing account",
    "existing details",
    "existing banking instructions",
    "existing bank instructions",
    "existing payment account",
    "remains unchanged",
    "remain unchanged",
    "no changes are required",
    "no change is required",
    "no changes required",
    "no changes have been made",
    "no changes were made",
    "no change has been made",
    "no change was made",
    "unchanged",
    "continue using",
    "continue to use",
    "still on file",
    "is unchanged",
    "are unchanged",
    "no amendments are required",
    "no amendment is required",
)


# ============================================================
# HELPERS
# ============================================================

def contains_any(text, terms):
    return any(term in text for term in terms)


def add_factor(factors, name, points):
    factors.append({
        "name": name,
        "score": points,
        "points": points,
    })


# ============================================================
# URGENCY DETECTION
# ============================================================

def has_urgency(message):
    message = message.lower()

    if contains_any(message, URGENCY_TERMS):
        return True

    deadline_patterns = (
        r"\bpay\s+today\b",
        r"\bpayment\s+today\b",
        r"\btransfer\s+today\b",
        r"\bsend\s+(?:the\s+)?(?:funds|money)\s+today\b",
        r"\bsettle\s+today\b",
        r"\bpay\s+tomorrow\b",
        r"\bpayment\s+tomorrow\b",
        r"\btransfer\s+tomorrow\b",
        r"\bsettle\s+tomorrow\b",
        r"\bdue\s+today\b",
        r"\bdue\s+tomorrow\b",
        r"\bdeadline\s+(?:is\s+)?today\b",
        r"\bdeadline\s+(?:is\s+)?tomorrow\b",
    )

    return any(
        re.search(pattern, message)
        for pattern in deadline_patterns
    )


# ============================================================
# BENEFICIARY / PAYMENT DESTINATION CHANGE
# ============================================================

def has_beneficiary_change(message):
    message = message.lower()

    # Stability override.
    # Prevents legitimate messages such as:
    # "No changes have been made to our banking details."
    if contains_any(message, STABILITY_TERMS):
        return False

    # Explicit beneficiary change.
    if contains_any(message, BENEFICIARY_CHANGE_TERMS):
        return True

    # Explicit banking-detail change.
    banking_change_terms = (
        "changed banking details",
        "changed our banking details",
        "banking details have changed",
        "updated banking details",
        "updated our banking details",
        "banking details have been updated",
        "new banking details",
        "new bank details",
        "changed bank details",
        "changed our bank details",
        "bank details have changed",
        "updated bank details",
        "updated our bank details",
        "bank details have been updated",
    )

    if contains_any(message, banking_change_terms):
        return True

    # Bank account change.
    bank_account_change_patterns = (
        r"\bbank\s+account\s+has\s+changed\b",
        r"\bbank\s+account\s+changed\b",
        r"\bbank\s+account\s+has\s+been\s+changed\b",
        r"\bchanged\s+our\s+bank\s+account\b",
        r"\bchanged\s+the\s+bank\s+account\b",
        r"\bupdate\s+our\s+bank\s+account\b",
        r"\bupdate\s+the\s+bank\s+account\b",
        r"\bupdated\s+our\s+bank\s+account\b",
        r"\bupdated\s+the\s+bank\s+account\b",
        r"\bnew\s+bank\s+account\b",
    )

    if any(
        re.search(pattern, message)
        for pattern in bank_account_change_patterns
    ):
        return True

    # Strong payment destination change.
    strong_destination_terms = (
        "payment destination",
        "receiving account",
        "receiving details",
        "payment recipient",
        "banking recipient",
        "remittance destination",
        "payment account",
    )

    if contains_any(message, strong_destination_terms):
        if contains_any(message, DESTINATION_CHANGE_TERMS):
            return True

    # Account replacement.
    account_replacement_patterns = (
        r"\breplace\s+the\s+account\b",
        r"\breplace\s+the\s+account\s+currently\s+used\b",
        r"\breplace\s+our\s+account\b",
        r"\breplace\s+the\s+bank\s+account\b",
        r"\baccount\s+replacement\b",
    )

    if any(
        re.search(pattern, message)
        for pattern in account_replacement_patterns
    ):
        return True

    # Payment to a new account.
    payment_to_new_account_patterns = (
        r"\b(?:send|pay|transfer|direct)\b"
        r".{0,80}"
        r"\b(?:the\s+)?(?:payment|funds|money)\b"
        r".{0,80}"
        r"\bto\s+the\s+new\s+account\b",

        r"\b(?:send|pay|transfer|direct)\b"
        r".{0,80}"
        r"\bthe\s+new\s+account\b",

        r"\b(?:payment|funds|money)\b"
        r".{0,80}"
        r"\bto\s+the\s+new\s+account\b",

        r"\binvoice\b"
        r".{0,80}"
        r"\bto\s+the\s+new\s+account\b",
    )

    if any(
        re.search(pattern, message)
        for pattern in payment_to_new_account_patterns
    ):
        return True

    # Indirect redirection.
    for route in REDIRECTION_TERMS:
        for target in REDIRECTION_TARGET_TERMS:
            pattern = (
                rf"\b{re.escape(route)}\b"
                rf".{{0,80}}"
                rf"\b{re.escape(target)}\b"
            )

            if re.search(pattern, message):
                if contains_any(message, REDIRECTION_MARKERS):
                    return True

    # Remittance destination change.
    if (
        re.search(r"\bremittances?\b", message)
        and re.search(
            r"\b(?:new|updated|changed|revised|different|alternative)"
            r"\s+destination\b",
            message,
        )
    ):
        return True

    return False


# ============================================================
# MESSAGE ANALYSIS
# ============================================================

def analyze_message(message):
    message_lower = message.lower()

    score = 0
    warnings = []
    factors = []

    stable = contains_any(
        message_lower,
        STABILITY_TERMS
    )

    # --------------------------------------------------------
    # BANKING DETAILS
    # --------------------------------------------------------

    if (
        contains_any(message_lower, BANKING_TERMS)
        and not stable
    ):
        score += 30

        warnings.append(
            "Banking details referenced"
        )

        add_factor(
            factors,
            "Banking details change",
            30
        )

    # --------------------------------------------------------
    # URGENCY
    # --------------------------------------------------------

    if has_urgency(message_lower):
        score += 15

        warnings.append(
            "Urgent payment request detected"
        )

        add_factor(
            factors,
            "Urgency",
            15
        )

    # --------------------------------------------------------
    # PAYMENT INTENT
    # --------------------------------------------------------

    payment_intent = contains_any(
        message_lower,
        PAYMENT_TERMS + FINANCIAL_OBLIGATION_TERMS
    )

    if payment_intent:
        score += 15

        add_factor(
            factors,
            "Payment-related request",
            15
        )

    # --------------------------------------------------------
    # FINANCIAL OBLIGATION
    # --------------------------------------------------------

    financial_obligation = contains_any(
        message_lower,
        FINANCIAL_OBLIGATION_TERMS
    )

    if (
        financial_obligation
        and not payment_intent
    ):
        score += 10

        add_factor(
            factors,
            "Financial obligation",
            10
        )

    # --------------------------------------------------------
    # BENEFICIARY / DESTINATION CHANGE
    # --------------------------------------------------------

    beneficiary_change = has_beneficiary_change(
        message_lower
    )

    if beneficiary_change:
        score += 10

        warnings.append(
            "Payment destination may have changed"
        )

        add_factor(
            factors,
            "Beneficiary change",
            10
        )

    # --------------------------------------------------------
    # CONTEXTUAL DESTINATION CHANGE
    # --------------------------------------------------------

    if (
        beneficiary_change
        and payment_intent
    ):
        score += 10

        add_factor(
            factors,
            "Payment destination change",
            10
        )

    # --------------------------------------------------------
    # URGENT DESTINATION CHANGE
    # --------------------------------------------------------

    if (
        beneficiary_change
        and has_urgency(message_lower)
    ):
        score += 10

        add_factor(
            factors,
            "Urgent destination change",
            10
        )

    return score, warnings, factors


# ============================================================
# SUPPLIER VERIFICATION
# ============================================================

def check_supplier(message, supplier):
    warnings = []
    factors = []
    supplier_score = 0

    # --------------------------------------------------------
    # EXTRACT SENDER EMAIL
    # --------------------------------------------------------

    sender_match = re.search(
        r"from:\s*(?:.*?<)?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        message,
        re.IGNORECASE
    )

    if sender_match:
        sender_email = sender_match.group(1).lower().strip()
        trusted_email = supplier["email"].lower().strip()

        print("DEBUG SENDER:", repr(sender_email))
        print("DEBUG TRUSTED:", repr(trusted_email))
        print(
            "DEBUG MATCH:",
            sender_email == trusted_email
        )

        # ----------------------------------------------------
        # TRUSTED SENDER
        # ----------------------------------------------------

        if sender_email == trusted_email:
            warnings.append(
                "Sender matches trusted supplier email"
            )

        # ----------------------------------------------------
        # UNTRUSTED / MISMATCHED SENDER
        # ----------------------------------------------------

        else:
            supplier_score += 20

            add_factor(
                factors,
                "Supplier email mismatch",
                20
            )

            warnings.append(
                "Sender does not match trusted supplier email"
            )

    # --------------------------------------------------------
    # EXTRACT REQUESTED ACCOUNT NUMBER
    # --------------------------------------------------------

    account_match = re.search(
        r"(?:account\s*(?:number|no\.?)?|a/c)\s*[:#]?\s*(\d{4,})",
        message,
        re.IGNORECASE
    )

    requested_account = None

    if account_match:
        full_requested_account = account_match.group(1)

        # CyberGuard stores only the last four digits.
        requested_account = full_requested_account[-4:]

        trusted_account = str(
            supplier["account_last_four"]
        ).strip()[-4:]

        print(
            "DEBUG REQUESTED ACCOUNT:",
            repr(requested_account)
        )

        print(
            "DEBUG TRUSTED ACCOUNT:",
            repr(trusted_account)
        )

        print(
            "DEBUG ACCOUNT MATCH:",
            requested_account == trusted_account
        )

        # ----------------------------------------------------
        # ACCOUNT MISMATCH
        # ----------------------------------------------------

        if requested_account != trusted_account:
            supplier_score += 25

            add_factor(
                factors,
                "Account mismatch",
                25
            )

            warnings.append(
                f"Requested account ending {requested_account} "
                f"does not match trusted supplier account"
            )

        # ----------------------------------------------------
        # ACCOUNT MATCH
        # ----------------------------------------------------

        else:
            warnings.append(
                "Requested account matches trusted supplier account"
            )

    return (
        supplier_score,
        warnings,
        factors,
        requested_account
    )


# ============================================================
# COMPLETE TRANSACTION ANALYSIS
# ============================================================

def analyze_transaction(message, supplier):

    # --------------------------------------------------------
    # MESSAGE ANALYSIS
    # --------------------------------------------------------

    (
        message_score,
        message_warnings,
        message_factors
    ) = analyze_message(message)

    # --------------------------------------------------------
    # SUPPLIER ANALYSIS
    # --------------------------------------------------------

    (
        supplier_score,
        supplier_warnings,
        supplier_factors,
        requested_account
    ) = check_supplier(
        message,
        supplier
    )

    # --------------------------------------------------------
    # FINAL DETERMINISTIC SCORE
    # --------------------------------------------------------

    score = min(
        message_score + supplier_score,
        100
    )

    # --------------------------------------------------------
    # WARNINGS
    # --------------------------------------------------------

    warnings = (
        message_warnings
        + supplier_warnings
    )

    # --------------------------------------------------------
    # RISK FACTORS
    # --------------------------------------------------------

    factors = (
        message_factors
        + supplier_factors
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
    # DEBUG OUTPUT
    # --------------------------------------------------------

    print("=" * 60)
    print("CYBERGUARD DETERMINISTIC ANALYSIS")
    print("MESSAGE SCORE:", message_score)
    print("SUPPLIER SCORE:", supplier_score)
    print("FINAL SCORE:", score)
    print("RISK LEVEL:", risk_level)
    print("WARNINGS:", warnings)
    print("FACTORS:", factors)
    print("REQUESTED ACCOUNT:", requested_account)
    print("=" * 60)

    return (
        score,
        risk_level,
        warnings,
        factors
    )