import re
# ============================================================
# PAYMENT CONTEXT
# ============================================================

PAYMENT_CONTEXT = [
    "scheduled payment",
    "future payment",
    "future payments",
    "payment is due",
    "payment due",
    "payment required",
    "payment instructions",
    "payment instruction",
    "payment request",
    "existing payment account",
]

# ============================================================
# PAYMENT ACTIONS
# ============================================================

PAYMENT_ACTIONS = [
    "make payment",
    "make a payment",
    "submit payment",
    "submit a payment",
    "send payment",
    "send a payment",
    "pay",
    "transfer",
    "wire transfer",
    "remittance",
    "remit",
    "send funds",
    "send money",
    "settle",
    "settlement",
    "eft",
]


# ============================================================
# FINANCIAL DOCUMENTS
# ============================================================

FINANCIAL_DOCUMENTS = [
    "invoice",
    "statement",
    "purchase order",
    "credit note",
    "debit note",
]


# ============================================================
# BANKING INFORMATION
# ============================================================

BANKING_SIGNALS = [
    "banking details",
    "banking information",
    "bank details",
    "bank account",
    "account number",
    "account details",
    "new account",
    "changed account",
    "change of account",
    "change bank",
    "new bank",
    "beneficiary",
]
AMBIGUOUS_FINANCIAL_SIGNALS = [
    "account information",
    "account update",
    "account updates",
    "account profile",
    
]

# ============================================================
# FINANCIAL OBLIGATIONS
# ============================================================

FINANCIAL_OBLIGATIONS = [
    "outstanding balance",
    "outstanding amount",
    "amount due",
    "balance due",
    "amount owing",
    "money owed",
    "funds",
    "invoice due",
    "invoice is due",
    "payment terms",
    "normal payment terms",
]


# ============================================================
# URGENCY
# ============================================================

URGENCY_SIGNALS = [
    "urgent",
    "urgently",
    "immediately",
    "as soon as possible",
    "today",
    "right away",
    "without delay",
]

# ============================================================
# FINANCIAL ACTIVITY
# ============================================================

FINANCIAL_ACTIVITY = [
    "payment confirmation",
    "payment received",
    "payment processed",
    "payment completed",
    "payment approved",
    "payment pending",
    "payment status",
    "payment history",
    "payment record",
    "payment records",
    "invoice records",
    "invoice received",
    "invoice attached",
    "invoice submitted",
    "invoice approved",
    "invoice processed",
    "statement received",
    "statement attached",
]
def contains_signal(text, signal):
    """
    Check whether a signal appears as a complete word/phrase.

    This prevents false matches such as:

        pay -> payroll
        remit -> remittance
    """

    if " " in signal:
        return signal in text

    pattern = rf"\b{re.escape(signal)}\b"
    return re.search(pattern, text) is not None


def find_signals(text, signals):
    """
    Return all matching signals from a signal group.
    """

    return [
        signal
        for signal in signals
        if contains_signal(text, signal)
    ]


def triage_email(email):
    """
    Classify an email into:

        IRRELEVANT
        UNCERTAIN
        PAYMENT_RELATED

    Triage determines whether an email should enter
    CyberGuard's deeper payment-fraud analysis pipeline.
    """

    subject = email.get("subject", "")
    body = email.get("body", "")

    text = f"{subject} {body}".lower()

    payment_actions = find_signals(text, PAYMENT_ACTIONS)
    payment_context = find_signals(text, PAYMENT_CONTEXT)
    financial_documents = find_signals(text, FINANCIAL_DOCUMENTS)
    banking_signals = find_signals(text, BANKING_SIGNALS)
    financial_obligations = find_signals(text, FINANCIAL_OBLIGATIONS)
    financial_activity = find_signals(text, FINANCIAL_ACTIVITY)
    urgency_signals = find_signals(text, URGENCY_SIGNALS)
    ambiguous_financial_signals = find_signals(
    text,
    AMBIGUOUS_FINANCIAL_SIGNALS
)

    # ========================================================
    # STRONG PAYMENT INTENT
    # ========================================================

    # Explicit payment action
    if payment_actions or payment_context:
        return {
            "category": "PAYMENT_RELATED",
            "reason": "An explicit financial action was detected.",
            "signals": (
                payment_actions
                + payment_context
                + financial_documents
                + banking_signals
                + financial_obligations
                + urgency_signals
            ),
        }
    
    # Financial obligation + banking information
    if financial_obligations and banking_signals:
        return {
            "category": "PAYMENT_RELATED",
            "reason": "A financial obligation is associated with banking information.",
            "signals": (
                financial_obligations
                + banking_signals
                + urgency_signals
            ),
        }

    # Financial obligation by itself
    if financial_obligations:
        return {
            "category": "PAYMENT_RELATED",
            "reason": "A financial obligation requiring settlement was detected.",
            "signals": (
                financial_obligations
                + urgency_signals
            ),
        }
     # ========================================================
# FINANCIAL ACTIVITY
# ========================================================

    if financial_activity:
        return {
        "category": "PAYMENT_RELATED",
        "reason": "Financial transaction or payment activity was detected.",
        "signals": (
            financial_activity
            + financial_documents
            + banking_signals
            + financial_obligations
            + urgency_signals
        ),
    }
    # ========================================================
    # FINANCIAL DOCUMENT + BANKING INFORMATION
    # ========================================================

    if financial_documents and banking_signals:
        return {
            "category": "PAYMENT_RELATED",
            "reason": "Financial document activity is associated with banking information.",
            "signals": (
                financial_documents
                + banking_signals
                + urgency_signals
            ),
        }

    # ========================================================
    # UNCERTAIN
    # ========================================================

    # Financial document without an explicit financial action
    if financial_documents:
        return {
            "category": "UNCERTAIN",
            "reason": "A financial document was mentioned, but no clear financial action was detected.",
            "signals": financial_documents,
        }

    # Banking information without payment intent
    if banking_signals:
        return {
            "category": "UNCERTAIN",
            "reason": "Banking information was mentioned, but no clear payment action was detected.",
            "signals": banking_signals,
        }
    if ambiguous_financial_signals:
        return {
        "category": "UNCERTAIN",
        "reason": "Potentially financial account activity was detected, but the purpose is unclear.",
        "signals": ambiguous_financial_signals,
    }
    # Urgency alone should NOT make something payment-related
   # Urgency alone is not enough to make an email
# payment-related.
#
# Example:
# "URGENT: Please review our supplier profile."
#
# This should remain irrelevant.

    if urgency_signals:
        return {
        "category": "IRRELEVANT",
        "reason": "Urgency was detected, but no meaningful payment-related intent was found.",
        "signals": [],
    }

    # ========================================================
    # IRRELEVANT
    # ========================================================

    return {
        "category": "IRRELEVANT",
        "reason": "No meaningful payment-related signals detected.",
        "signals": [],
    }
    