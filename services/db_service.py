# services/db_service.py

import sqlite3
import pandas as pd

DB_PATH = "crm_database.db"


def get_connection():

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    return conn


def get_all(table):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df


def append_row(table, data):
    conn = get_connection()

    columns = ",".join(data.keys())
    placeholders = ",".join(["?"] * len(data))
    values = list(data.values())

    conn.execute(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
        values,
    )

    conn.commit()
    conn.close()


def update_row(table, column, value, data):

    conn = get_connection()

    updates = ",".join([f"{k}=?" for k in data.keys()])
    values = list(data.values())
    values.append(value)

    conn.execute(
        f"UPDATE {table} SET {updates} WHERE {column}=?",
        values,
    )

    conn.commit()
    conn.close()