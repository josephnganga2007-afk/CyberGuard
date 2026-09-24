from database import initialize_database, save_transaction


initialize_database()


# =========================
# ABC SUPPLIES
# =========================

save_transaction(
    "ABC Supplies",
    "Invoice #1001. Please process payment to account 4821.",
    15,
    "LOW",
    "4821",
    "BASELINE"
)

save_transaction(
    "ABC Supplies",
    "Invoice #1002. Payment is due according to the attached invoice. Account 4821.",
    15,
    "LOW",
    "4821",
    "BASELINE"
)

save_transaction(
    "ABC Supplies",
    "Please process invoice #1003 using our usual account 4821.",
    15,
    "LOW",
    "4821",
    "BASELINE"
)


# =========================
# XYZ TRADERS
# =========================

save_transaction(
    "XYZ Traders",
    "Invoice #2001. Please process payment to account 7319.",
    15,
    "LOW",
    "7319",
    "BASELINE"
)

save_transaction(
    "XYZ Traders",
    "Payment for invoice #2002 is due. Please use account 7319.",
    15,
    "LOW",
    "7319",
    "BASELINE"
)


# =========================
# TECHCORP
# =========================

save_transaction(
    "TechCorp",
    "Invoice #3001. Please process payment using account 9042.",
    15,
    "LOW",
    "9042",
    "BASELINE"
)

save_transaction(
    "TechCorp",
    "Please process invoice #3002 using our usual account 9042.",
    15,
    "LOW",
    "9042",
    "BASELINE"
)


print("Legitimate historical baseline created.")