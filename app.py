# path: app.py

import streamlit as st
from services.db_init import initialize_database
import time
from services.backup_service import backup_database

st.set_page_config(
    page_title="Signaasat CRM",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

from services.db_init import initialize_database
initialize_database()


st.title("Signaasat CRM")
    
if "last_backup" not in st.session_state:
    st.session_state.last_backup = 0

if time.time() - st.session_state.last_backup > 1800:
    backup_database()
    st.session_state.last_backup = time.time()

st.markdown("### Use the sidebar to navigate the CRM modules.")

from services.backup_service import backup_database, get_last_backup_time
import datetime

# ========================
# AUTO BACKUP (5 MIN LOGIC)
# ========================

now = datetime.datetime.utcnow()
last_backup = get_last_backup_time()

if last_backup is None:
    backup_database()

else:
    diff_minutes = (now - last_backup).total_seconds() / 60

    if diff_minutes >= 5:
        backup_database()