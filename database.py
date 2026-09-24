import sqlite3


DATABASE = "cyberguard.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Supplier table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            account_last_four TEXT NOT NULL
        )
    """)

    # Transaction history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        message TEXT NOT NULL,
        risk_score INTEGER NOT NULL,
        risk_level TEXT NOT NULL,
        requested_account TEXT,
        transaction_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    conn.commit()
    conn.close()


def add_supplier(name, email, account_last_four):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO suppliers
        (name, email, account_last_four)
        VALUES (?, ?, ?)
    """, (
        name,
        email,
        account_last_four
    ))

    conn.commit()
    conn.close()


def get_supplier(name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, email, account_last_four
        FROM suppliers
        WHERE name = ?
        LIMIT 1
    """, (name,))

    supplier = cursor.fetchone()

    conn.close()

    if supplier:

        return {
            "name": supplier[0],
            "email": supplier[1],
            "account_last_four": supplier[2]
        }

    return None


def get_all_suppliers():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name
        FROM suppliers
        GROUP BY name
        ORDER BY name
    """)

    suppliers = cursor.fetchall()

    conn.close()

    return suppliers


def save_transaction(
    supplier_name,
    message,
    risk_score,
    risk_level,
    requested_account,
    transaction_type="LIVE"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (
            supplier_name,
            message,
            risk_score,
            risk_level,
            requested_account,
            transaction_type
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        supplier_name,
        message,
        risk_score,
        risk_level,
        requested_account,
        transaction_type
    ))

    conn.commit()
    conn.close()

def get_supplier_history(supplier_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            message,
            risk_score,
            risk_level,
            requested_account,
            transaction_type,
            created_at
        FROM transactions
        WHERE supplier_name = ?
        ORDER BY id DESC
    """, (supplier_name,))

    history = cursor.fetchall()

    conn.close()

    return history

def get_transaction_stats():

    conn = get_connection()
    cursor = conn.cursor()

    # Total transactions
    cursor.execute("""
        SELECT COUNT(*)
        FROM transactions
    """)

    total_transactions = cursor.fetchone()[0]

    # High / Critical transactions
    cursor.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE risk_level IN ('HIGH', 'CRITICAL')
    """)

    high_risk_transactions = cursor.fetchone()[0]

    # Trusted suppliers
    cursor.execute("""
        SELECT COUNT(DISTINCT name)
        FROM suppliers
    """)

    total_suppliers = cursor.fetchone()[0]

    conn.close()

    return {
        "total_transactions": total_transactions,
        "high_risk_transactions": high_risk_transactions,
        "total_suppliers": total_suppliers
    }

def get_recent_transactions(limit=10):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            supplier_name,
            risk_score,
            risk_level,
            requested_account,
            created_at
        FROM transactions
        WHERE transaction_type = 'LIVE'
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    transactions = cursor.fetchall()

    conn.close()

    return transactions    


def get_supplier_risk_trend(supplier_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            risk_score,
            risk_level,
            created_at
        FROM transactions
        WHERE supplier_name = ?
        ORDER BY id ASC
    """, (supplier_name,))

    trend = cursor.fetchall()

    conn.close()

    return trend    

def get_supplier_trust_score(supplier_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            risk_score,
            transaction_type
        FROM transactions
        WHERE supplier_name = ?
        ORDER BY id DESC
    """, (supplier_name,))

    transactions = cursor.fetchall()
    conn.close()

    live_scores = [
        transaction[0]
        for transaction in transactions
        if transaction[1] == "LIVE"
    ]

    if not live_scores:
        return {
            "score": 100,
            "label": "NEW SUPPLIER",
            "description": "No transaction history available yet."
        }

    # Calculate the average historical risk.
    average_risk = sum(live_scores) / len(live_scores)

    # Convert risk into trust.
    score = round(100 - average_risk)

    score = max(0, min(score, 100))

    if score >= 80:
        label = "HIGH TRUST"
        description = (
            "Supplier behaviour has remained largely consistent."
        )
    elif score >= 60:
        label = "MODERATE TRUST"
        description = (
            "Some unusual activity has been detected."
        )
    else:
        label = "LOW TRUST"
        description = (
            "Supplier history contains significant risk signals."
        )

    return {
        "score": score,
        "label": label,
        "description": description
    }