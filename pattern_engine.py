import re


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
)

FINANCIAL_OBLIGATION_TERMS = (
    "outstanding balance",
    "outstanding amount",
    "amount due",
    "balance due",
    "amount owing",
    "money owed",
)

BENEFICIARY_CHANGE_TERMS = (
    "new beneficiary",
    "new beneficiary details",
    "updated beneficiary",
    "updated beneficiary details",
    "changed beneficiary",
    "changed beneficiary details",
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

PAYMENT_DESTINATION_TERMS = (
    "beneficiary",
    "payment destination",
    "receiving account",
    "receiving details",
    "payment recipient",
    "banking recipient",
    "remittance destination",
    "payment details",
    "bank instructions",
    "banking instructions",
    "settlement account",
    "settlement details",
    "payment route",
    "payment account",
    "account used for payments",
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
    "information",
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


def contains_any(text, terms):
    return any(term in text for term in terms)


def has_urgency(message):
    """
    Behavioural urgency means explicit pressure,
    not ordinary dates such as 'today' or 'tomorrow'.
    """
    message = message.lower()
    return contains_any(message, URGENCY_TERMS)


def get_account_number(message):
    match = re.search(
        r"(?:account|account number|a/c)\s*(?:is|:)?\s*(\d{4,})",
        message.lower()
    )

    if match:
        return match.group(1)[-4:]

    return None


def has_beneficiary_change(message):
    message = message.lower()

    # Explicit beneficiary-change language
    if contains_any(message, BENEFICIARY_CHANGE_TERMS):
        return True

    # Explicit banking-detail changes only.
    # A mere mention of banking details is NOT a behavioural change.
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

    # Strong payment-destination concepts
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

    # Indirect redirection language
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

    # Remittance destination change
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


def analyze_pattern(message, history):
    """
    Compare the current communication against the supplier's
    historical baseline.

    IMPORTANT:
    This function produces behavioural deviations only.
    It does NOT modify the deterministic risk score.
    """

    baseline = [
        transaction
        for transaction in history
        if transaction[5] == "BASELINE"
    ]

    if not baseline:
        return {
            "deviation_score": 0,
            "warnings": [],
            "deviations": [],
        }

    message_lower = message.lower()

    warnings = []
    deviations = []

    # ---------------------------------------------------------
    # ACCOUNT CHANGE
    # ---------------------------------------------------------

    accounts = []

    for transaction in baseline:
        account = transaction[4]

        if account:
            accounts.append(account)

    normal_account = None

    if accounts:
        normal_account = max(
            set(accounts),
            key=accounts.count
        )

    requested_account = get_account_number(message)

    if (
        requested_account
        and normal_account
        and requested_account != normal_account
    ):
        deviations.append({
            "type": "Account change",
            "normal": normal_account,
            "current": requested_account,
        })

        warnings.append(
            f"Supplier normally uses account {normal_account}, "
            f"but this request specifies account {requested_account}"
        )

    # ---------------------------------------------------------
    # BANKING / BENEFICIARY CHANGE
    # ---------------------------------------------------------

    if has_beneficiary_change(message_lower):
        deviations.append({
            "type": "Banking detail change",
            "normal": "Existing supplier banking details",
            "current": "New or changed banking details",
        })

        warnings.append(
            "Banking or payment-destination behaviour "
            "differs from the supplier's normal pattern"
        )

    # ---------------------------------------------------------
    # URGENCY CHANGE
    # ---------------------------------------------------------

    if has_urgency(message_lower):
        deviations.append({
            "type": "Urgency change",
            "normal": "Routine communication",
            "current": "Urgent request",
        })

        warnings.append(
            "Urgency level differs from the supplier's "
            "usual communication pattern"
        )

    # ---------------------------------------------------------
    # DEVIATION SCORE
    # ---------------------------------------------------------

    deviation_count = len(deviations)

    if deviation_count == 0:
        deviation_score = 0

    elif deviation_count == 1:
        deviation_score = 10

    elif deviation_count == 2:
        deviation_score = 15

    else:
        deviation_score = 20

    return {
        "deviation_score": deviation_score,
        "warnings": warnings,
        "deviations": deviations,
    }