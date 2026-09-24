import re


def get_account_number(message):

    match = re.search(
        r"(?:account|account number|a/c)\s*(?:is|:)?\s*(\d{4,})",
        message.lower()
    )

    if match:
        return match.group(1)[-4:]

    return None


def analyze_pattern(message, history):

    # Only use legitimate historical transactions
    baseline = [
        transaction
        for transaction in history
        if transaction[5] == "BASELINE"
    ]

    if not baseline:

        return {
            "deviation_score": 0,
            "warnings": [],
            "deviations": []
        }

    message_lower = message.lower()

    warnings = []
    deviations = []

    # ---------------------------------
    # Establish normal supplier account
    # ---------------------------------

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

    # ---------------------------------
    # Compare requested account
    # ---------------------------------

    requested_account = get_account_number(message)

    if (
        requested_account
        and normal_account
        and requested_account != normal_account
    ):

        deviations.append({
            "type": "Account change",
            "normal": normal_account,
            "current": requested_account
        })

        warnings.append(
            f"Supplier normally uses account {normal_account}, "
            f"but this request specifies account {requested_account}"
        )

    # ---------------------------------
    # Banking-detail behaviour
    # ---------------------------------

    if (
        "banking details" in message_lower
        or "bank details" in message_lower
    ):

        deviations.append({
            "type": "Banking detail change",
            "normal": "Established details",
            "current": "Change requested"
        })

        warnings.append(
            "Banking details are being changed from the "
            "supplier's established behaviour"
        )

    # ---------------------------------
    # Urgency behaviour
    # ---------------------------------

    urgency_words = [
        "urgent",
        "immediately",
        "today",
        "as soon as possible"
    ]

    urgency_detected = any(
        word in message_lower
        for word in urgency_words
    )

    if urgency_detected:

        deviations.append({
            "type": "Urgency change",
            "normal": "Routine communication",
            "current": "Urgent request"
        })

        warnings.append(
            "Urgency level differs from the supplier's "
            "usual communication pattern"
        )

    # ---------------------------------
    # Calculate behavioural score
    # ---------------------------------

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
        "deviations": deviations
    }