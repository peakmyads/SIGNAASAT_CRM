import sqlite3

DB_PATH = "crm_database.db"

def initialize_database():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Clients (
        client_id TEXT,
        client_name TEXT,
        client_type TEXT,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        gstin TEXT,
        start_date TEXT,
        monthly_fee REAL,
        package_details TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Editors (
        editor_id TEXT,
        editor_name TEXT,
        phone TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Work_Assignments (
        task_id TEXT,
        client_id TEXT,
        client_name TEXT,
        work_type TEXT,
        editor TEXT,
        status TEXT,
        month TEXT,
        video_url TEXT,
        ad_budget TEXT,
        created_date TEXT,
        completed_date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Billing (
        invoice_no TEXT,
        client_id TEXT,
        client_name TEXT,
        month TEXT,
        amount REAL,
        invoice_date TEXT,
        payment_status TEXT,
        payment_date TEXT,
        payment_mode TEXT,
        payment_amount REAL
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Expenses (
        expense_id TEXT,
        date TEXT,
        category TEXT,
        description TEXT,
        amount REAL,
        payment_mode TEXT,
        notes TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Social_Insights (
        date TEXT,
        platform TEXT,
        impressions INTEGER,
        reach INTEGER,
        clicks INTEGER,
        conversions INTEGER,
        spend REAL
    )
    """)

    conn.commit()
    conn.close()