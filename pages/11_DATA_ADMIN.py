import streamlit as st
import pandas as pd

from services.db_service import get_all, update_row

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛠 Admin Data Editor")

st.markdown("""
<style>

/* Base button */
div.stButton > button {
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 15px;
    transition: all 0.25s ease;
}

/* PRIMARY (Save Changes) */
button[kind="primary"] {
    background: linear-gradient(90deg,#6a5cff,#8f7bff);
    color: white;
    border: none;
}

button[kind="primary"]:hover {
    background: linear-gradient(90deg,#5948ff,#7b68ff);
    transform: scale(1.03);
}

/* SECONDARY (Download) */
button[kind="secondary"] {
    background-color: #e089df;
    color: #333;
    border: 1px solid #dcdcdc;
}

button[kind="secondary"]:hover {
    background-color: #e2e6ea;
}

/* DANGER (Restore) */
button[kind="secondary"][data-testid*="Restore"] {
    background-color: #ffe3e3;
    color: #c92a2a;
    border: 1px solid #ffa8a8;
}

button[kind="secondary"][data-testid*="Restore"]:hover {
    background-color: #ffc9c9;
    transform: scale(1.02);
}

</style>
""", unsafe_allow_html=True)

# =========================
# SELECT TABLE
# =========================

table = st.selectbox(
    "Select Table",
    [
        "Clients",
        "Editors",
        "Work_Assignments",
        "Billing",
        "Expenses",
        "Social_Insights"
    ]
)

df = get_all(table)

if df.empty:
    st.warning("No data found")
    st.stop()

st.subheader(f"{table} Table")

# =========================
# EDIT DATA
# =========================

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True
)

# =========================
# SAVE CHANGES
# =========================

if st.button("💾 Save Changes", type="primary"):

    for i, row in edited_df.iterrows():

        original = df.iloc[i]

        if not row.equals(original):

            update_row(
                table,
                df.columns[0],
                original[df.columns[0]],
                row.to_dict()
            )

    st.success("Changes saved successfully!")

    # refresh cached data everywhere
    st.cache_data.clear()

    st.rerun()

# =========================
# EXPORT DATA
# =========================

st.download_button(
    "⬇ Download Excel",
    edited_df.to_csv(index=False),
    file_name=f"{table}.csv"
)

import os

st.divider()
st.subheader("💾 Database Backup")

db_file = "crm_database.db"

if os.path.exists(db_file):

    with open(db_file, "rb") as f:
        st.download_button(
            label="⬇ Download Full Database Backup",
            data=f,
            file_name="crm_database_backup.db",
            mime="application/octet-stream"
        )

else:
    st.warning("Database file not found.")
    
from services.backup_service import (
    backup_database,
    list_backups,
    restore_backup
)

st.divider()
st.subheader("💾 Backup Management")

st.markdown("<br>", unsafe_allow_html=True)

# 🔵 Backup Now
if st.button("🔄 Backup Now", type="secondary"):
    name = backup_database()
    st.success(f"Backup created: {name}")


# 📊 Backup Status
backups = list_backups()

st.write(f"📦 Total Backups: {len(backups)}")

if backups:
    st.write(f"🕒 Latest Backup: {backups[0]}")


from services.backup_service import (
    backup_database,
    list_backups,
    restore_backup,
    get_backup_details,
    download_backup
)

import datetime

# ========================
# HEALTH INDICATOR
# ========================
details = get_backup_details()

if details:
    latest = details[0].client_modified.replace(tzinfo=None)
    now = datetime.datetime.utcnow()

    diff = (now - latest).total_seconds() / 3600

    if diff < 1:
        st.success(f"🟢 Healthy (Last backup {round(diff,2)} hrs ago)")
    elif diff < 6:
        st.warning(f"🟡 Warning (Last backup {round(diff,2)} hrs ago)")
    else:
        st.error(f"🔴 Critical (Last backup {round(diff,2)} hrs ago)")
else:
    st.error("❌ No backups found")


# ========================
# BACKUP LIST
# ========================
backup_names = [f.name for f in details]

selected = st.selectbox("📂 Select Backup", backup_names)


# ========================
# DOWNLOAD BUTTON
# ========================
if st.button("⬇ Download Backup", type="secondary"):
    data = download_backup(selected)

    st.download_button(
        label="Click to Download",
        data=data,
        file_name=selected,
        mime="application/octet-stream"
    )


# ========================
# RESTORE BUTTON
# ========================
if st.button("⚠ Restore Selected Backup", type="secondary"):
    msg = restore_backup(selected)

    st.success(msg)

    st.session_state.pop("app_data", None)
    st.rerun()    
