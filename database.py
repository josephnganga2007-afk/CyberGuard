import sqlite3

DATABASE = "cyberguard.db"



def get_connection():

    conn=sqlite3.connect(DATABASE); conn.row_factory=sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON"); return conn



def initialize_database():

    conn=get_connection(); c=conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT,account_last_four TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT,supplier_name TEXT NOT NULL,message TEXT NOT NULL,risk_score INTEGER NOT NULL,risk_level TEXT NOT NULL,requested_account TEXT,transaction_type TEXT DEFAULT 'LIVE',created_at TEXT DEFAULT CURRENT_TIMESTAMP,gmail_message_id TEXT,business_id INTEGER)""")

    c.execute("""CREATE TABLE IF NOT EXISTS investigations (id INTEGER PRIMARY KEY AUTOINCREMENT,supplier_name TEXT NOT NULL,sender TEXT,subject TEXT,message TEXT NOT NULL,requested_account TEXT,risk_score INTEGER,risk_level TEXT,status TEXT DEFAULT 'PENDING',created_at TEXT DEFAULT CURRENT_TIMESTAMP,reviewed_at TEXT,review_decision TEXT,business_id INTEGER,gmail_message_id TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS businesses (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,gmail_account TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS business_suppliers (id INTEGER PRIMARY KEY AUTOINCREMENT,business_id INTEGER NOT NULL,supplier_id INTEGER NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(business_id,supplier_id),FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE,FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE)""")

    for sql in ("ALTER TABLE transactions ADD COLUMN gmail_message_id TEXT","ALTER TABLE transactions ADD COLUMN business_id INTEGER","ALTER TABLE investigations ADD COLUMN business_id INTEGER","ALTER TABLE investigations ADD COLUMN gmail_message_id TEXT","ALTER TABLE businesses ADD COLUMN gmail_account TEXT"):

        try: c.execute(sql)

        except sqlite3.OperationalError: pass

    for sql in ("CREATE INDEX IF NOT EXISTS idx_transactions_business ON transactions(business_id)","CREATE INDEX IF NOT EXISTS idx_transactions_gmail ON transactions(gmail_message_id)","CREATE INDEX IF NOT EXISTS idx_investigations_business ON investigations(business_id)","CREATE INDEX IF NOT EXISTS idx_investigations_gmail ON investigations(gmail_message_id)","CREATE INDEX IF NOT EXISTS idx_investigations_status ON investigations(status)"): c.execute(sql)

    conn.commit(); conn.close()



def add_supplier(name,email=None,account_last_four=None):

    conn=get_connection(); c=conn.cursor(); c.execute("INSERT INTO suppliers(name,email,account_last_four) VALUES(?,?,?)",(name,email,account_last_four)); i=c.lastrowid; conn.commit(); conn.close(); return i

def get_supplier(name):

    conn=get_connection(); r=conn.execute("SELECT * FROM suppliers WHERE name=? LIMIT 1",(name,)).fetchone(); conn.close(); return r

def get_all_suppliers():

    conn=get_connection(); r=conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall(); conn.close(); return r

def get_supplier_by_email(email):
    if not email:
        return None
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM suppliers WHERE LOWER(email)=LOWER(?) LIMIT 1",
        (email.strip(),)
    ).fetchone()
    conn.close()
    return row

def get_supplier_for_business(business_id, supplier_identifier):
    if not supplier_identifier:
        return None

    conn = get_connection()

    row = conn.execute(
        """
        SELECT s.*
        FROM suppliers s
        JOIN business_suppliers bs
            ON bs.supplier_id = s.id
        WHERE bs.business_id = ?
          AND (
                LOWER(s.name) = LOWER(?)
                OR LOWER(s.email) = LOWER(?)
              )
        LIMIT 1
        """,
        (
            business_id,
            supplier_identifier.strip(),
            supplier_identifier.strip()
        )
    ).fetchone()

    conn.close()

    if row is None:
        return None

    return dict(row)
def get_supplier_history(supplier_name,business_id=None):

    conn=get_connection()

    if business_id is None: r=conn.execute("SELECT * FROM transactions WHERE supplier_name=? ORDER BY created_at DESC",(supplier_name,)).fetchall()

    else: r=conn.execute("SELECT * FROM transactions WHERE supplier_name=? AND business_id=? ORDER BY created_at DESC",(supplier_name,business_id)).fetchall()

    conn.close(); return r



def save_transaction(supplier_name,message,risk_score,risk_level,requested_account=None,transaction_type="LIVE",gmail_message_id=None,business_id=None):

    conn=get_connection(); c=conn.cursor(); c.execute("INSERT INTO transactions(supplier_name,message,risk_score,risk_level,requested_account,transaction_type,gmail_message_id,business_id) VALUES(?,?,?,?,?,?,?,?)",(supplier_name,message,risk_score,risk_level,requested_account,transaction_type,gmail_message_id,business_id)); i=c.lastrowid; conn.commit(); conn.close(); return i

def gmail_message_exists(gmail_message_id,business_id=None):

    if not gmail_message_id:return False

    conn=get_connection()

    if business_id is None:r=conn.execute("SELECT id FROM transactions WHERE gmail_message_id=? LIMIT 1",(gmail_message_id,)).fetchone()

    else:r=conn.execute("SELECT id FROM transactions WHERE gmail_message_id=? AND business_id=? LIMIT 1",(gmail_message_id,business_id)).fetchone()

    conn.close(); return r is not None

def get_transaction_stats(business_id=None):

    conn=get_connection()

    if business_id is None: rows=conn.execute("SELECT risk_level,COUNT(*) count FROM transactions GROUP BY risk_level").fetchall()

    else: rows=conn.execute("SELECT risk_level,COUNT(*) count FROM transactions WHERE business_id=? GROUP BY risk_level",(business_id,)).fetchall()

    s={"total_transactions":0,"low_risk":0,"medium_risk":0,"high_risk_transactions":0,"critical_risk":0}

    for r in rows:

        n=r["count"]; s["total_transactions"]+=n

        if r["risk_level"]=="LOW":s["low_risk"]+=n

        elif r["risk_level"]=="MEDIUM":s["medium_risk"]+=n

        elif r["risk_level"]=="HIGH":s["high_risk_transactions"]+=n

        elif r["risk_level"]=="CRITICAL":s["critical_risk"]+=n

    conn.close(); return s

def get_recent_transactions(limit=50,business_id=None):

    conn=get_connection()

    if business_id is None:r=conn.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()

    else:r=conn.execute("SELECT * FROM transactions WHERE business_id=? ORDER BY created_at DESC LIMIT ?",(business_id,limit)).fetchall()

    conn.close(); return r

def get_business_transactions(business_id,limit=50): return get_recent_transactions(limit,business_id)

def get_supplier_risk_trend(supplier_name,limit=10,business_id=None):

    conn=get_connection()

    if business_id is None:r=conn.execute("SELECT risk_score,risk_level,created_at FROM transactions WHERE supplier_name=? ORDER BY created_at DESC LIMIT ?",(supplier_name,limit)).fetchall()

    else:r=conn.execute("SELECT risk_score,risk_level,created_at FROM transactions WHERE supplier_name=? AND business_id=? ORDER BY created_at DESC LIMIT ?",(supplier_name,business_id,limit)).fetchall()

    conn.close(); return r

def get_supplier_trust_score(supplier_name,business_id=None):

    h=get_supplier_history(supplier_name,business_id)

    return 100 if not h else max(0,round(100-sum(x["risk_score"] for x in h)/len(h)))



def investigation_exists(gmail_message_id=None,business_id=None):

    if not gmail_message_id:return False

    conn=get_connection()

    if business_id is None:r=conn.execute("SELECT id FROM investigations WHERE gmail_message_id=? LIMIT 1",(gmail_message_id,)).fetchone()

    else:r=conn.execute("SELECT id FROM investigations WHERE gmail_message_id=? AND business_id=? LIMIT 1",(gmail_message_id,business_id)).fetchone()

    conn.close(); return r is not None

def save_investigation(
    supplier_name,
    sender,
    subject,
    message,
    requested_account,
    risk_score,
    risk_level,
    status="PENDING",
    business_id=None,
    gmail_message_id=None,
    triage_reason=None,
    triage_signals=None
):
    conn = get_connection()
    c = conn.cursor()

    # Convert signal lists into readable text for SQLite.
    if isinstance(triage_signals, (list, tuple)):
        triage_signals = ", ".join(str(signal) for signal in triage_signals)

    c.execute(
        """
        INSERT INTO investigations (
            supplier_name,
            sender,
            subject,
            message,
            requested_account,
            risk_score,
            risk_level,
            status,
            business_id,
            gmail_message_id,
            triage_reason,
            triage_signals
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            supplier_name,
            sender,
            subject,
            message,
            requested_account,
            risk_score,
            risk_level,
            status,
            business_id,
            gmail_message_id,
            triage_reason,
            triage_signals
        )
    )

    investigation_id = c.lastrowid

    conn.commit()
    conn.close()

    return investigation_id
def get_pending_investigations(business_id=None):

    conn=get_connection()

    if business_id is None:r=conn.execute("SELECT * FROM investigations WHERE status='PENDING' ORDER BY created_at DESC").fetchall()

    else:r=conn.execute("SELECT * FROM investigations WHERE status='PENDING' AND business_id=? ORDER BY created_at DESC",(business_id,)).fetchall()

    conn.close(); return r

def review_investigation(investigation_id,decision,reviewer_notes=None,business_id=None):

    d=decision.upper()

    if d=="LEGITIMATE": status="APPROVE"

    elif d=="SUSPICIOUS": status="REJECT"

    elif d in ("APPROVE","REJECT"): status=d

    else:return False

    stored=f"{status}: {reviewer_notes}" if reviewer_notes else status

    conn=get_connection(); c=conn.cursor()

    if business_id is None:c.execute("UPDATE investigations SET status=?,review_decision=?,reviewed_at=CURRENT_TIMESTAMP WHERE id=?",(status,stored,investigation_id))

    else:c.execute("UPDATE investigations SET status=?,review_decision=?,reviewed_at=CURRENT_TIMESTAMP WHERE id=? AND business_id=?",(status,stored,investigation_id,business_id))

    changed=c.rowcount>0; conn.commit(); conn.close(); return changed



def create_business(name,gmail_account=None):

    conn=get_connection(); c=conn.cursor(); c.execute("INSERT INTO businesses(name,gmail_account) VALUES(?,?)",(name,gmail_account)); i=c.lastrowid; conn.commit(); conn.close(); return i

def get_business_by_id(business_id):

    conn=get_connection(); r=conn.execute("SELECT * FROM businesses WHERE id=?",(business_id,)).fetchone(); conn.close(); return r

def get_business(business_id):return get_business_by_id(business_id)

def get_all_businesses():

    conn=get_connection(); r=conn.execute("SELECT * FROM businesses ORDER BY name").fetchall(); conn.close(); return r

def set_business_gmail_account(business_id,gmail_account):

    conn=get_connection(); conn.execute("UPDATE businesses SET gmail_account=? WHERE id=?",(gmail_account,business_id)); conn.commit(); conn.close()

def get_business_by_gmail_account(gmail_account):

    if not gmail_account:return None

    conn=get_connection(); r=conn.execute("SELECT * FROM businesses WHERE gmail_account=? LIMIT 1",(gmail_account,)).fetchone(); conn.close(); return r

def get_business_gmail(business_id):

    b=get_business_by_id(business_id); return b["gmail_account"] if b else None

def link_supplier_to_business(business_id,supplier_id):

    conn=get_connection(); conn.execute("INSERT OR IGNORE INTO business_suppliers(business_id,supplier_id) VALUES(?,?)",(business_id,supplier_id)); conn.commit(); conn.close()

def get_business_suppliers(business_id):

    conn=get_connection(); r=conn.execute("SELECT s.* FROM suppliers s JOIN business_suppliers bs ON bs.supplier_id=s.id WHERE bs.business_id=? ORDER BY s.name",(business_id,)).fetchall(); conn.close(); return r

def get_business_security_summary(business_id):

    conn=get_connection()

    total=conn.execute("SELECT COUNT(*) FROM transactions WHERE business_id=?",(business_id,)).fetchone()[0]

    high=conn.execute("SELECT COUNT(*) FROM transactions WHERE business_id=? AND risk_level='HIGH'",(business_id,)).fetchone()[0]

    critical=conn.execute("SELECT COUNT(*) FROM transactions WHERE business_id=? AND risk_level='CRITICAL'",(business_id,)).fetchone()[0]

    pending=conn.execute("SELECT COUNT(*) FROM investigations WHERE business_id=? AND status='PENDING'",(business_id,)).fetchone()[0]

    linked=conn.execute("SELECT COUNT(*) FROM business_suppliers WHERE business_id=?",(business_id,)).fetchone()[0]

    conn.close(); return {"total_transactions":total,"high_risk":high,"critical":critical,"pending_investigations":pending,"linked_suppliers":linked}

def get_business_investigations(business_id):

    conn=get_connection(); r=conn.execute("SELECT * FROM investigations WHERE business_id=? ORDER BY created_at DESC",(business_id,)).fetchall(); conn.close(); return r
