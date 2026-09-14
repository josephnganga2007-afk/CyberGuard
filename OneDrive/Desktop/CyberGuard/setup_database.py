from database import initialize_database, add_supplier

initialize_database()

add_supplier(
    "ABC Supplies",
    "accounts@abcsupplies.co.za",
    "4821"
)
add_supplier(
    "XYZ Traders",
    "accounts@xyztraders.co.za",
    "7319"
)

add_supplier(
    "TechCorp",
    "billing@techcorp.co.za",
    "9042"
)
print("Database ready.")