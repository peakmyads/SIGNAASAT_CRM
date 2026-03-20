import streamlit as st
import pandas as pd
from datetime import datetime
from services.db_service import update_row
from services.db_service import append_row
from services.data_loader import load_data

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

st.set_page_config(layout="wide")

import re

def normalize_url(url):
    url = str(url).strip().lower()

    # YouTube
    yt_match = re.search(r"(?:v=|youtu\.be/)([^&]+)", url)
    if yt_match:
        return f"youtube_{yt_match.group(1)}"

    # Instagram
    ig_match = re.search(r"instagram\.com/.+?/([^/?]+)", url)
    if ig_match:
        return f"instagram_{ig_match.group(1)}"

    return url

# =========================
# PAGE STYLE
# =========================

st.markdown("""
<style>

.page-title{
    font-size:34px;
    font-weight:700;
    margin-bottom:25px;
}

div.stButton > button{
    background:linear-gradient(90deg,#6a5cff,#8f7bff);
    color:white;
    border:none;
    border-radius:6px;
    padding:8px 18px;
    font-weight:600;
}

div.stButton > button:hover{
    background:linear-gradient(90deg,#5a4bff,#7b68ff);
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🎬 Editor Tasks</div>', unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================

data = load_data()

tasks_df = data["tasks"]
clients_df = data["clients"]

# Load Editors dynamically
try:
    editors_df = data["editors"]
    editor_list = editors_df["editor_name"].tolist()
except:
    editor_list = []

# =========================
# FINANCIAL YEAR LOGIC
# =========================

today = datetime.today()

if today.month >= 4:
    current_fy_start = today.year
else:
    current_fy_start = today.year - 1

current_fy = f"{current_fy_start}-{str(current_fy_start+1)[2:]}"
next_fy = f"{current_fy_start+1}-{str(current_fy_start+2)[2:]}"

fy_list = [current_fy, next_fy]


# =========================
# MONTH GENERATOR
# =========================

def get_month_list(fy):

    start_year = int(fy.split("-")[0])

    months = [
        ("Apr", start_year),
        ("May", start_year),
        ("Jun", start_year),
        ("Jul", start_year),
        ("Aug", start_year),
        ("Sep", start_year),
        ("Oct", start_year),
        ("Nov", start_year),
        ("Dec", start_year),
        ("Jan", start_year+1),
        ("Feb", start_year+1),
        ("Mar", start_year+1)
    ]

    return [f"{m}-{y}" for m, y in months]


# =========================
# FILTER BAR
# =========================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    editor = st.selectbox("Editor", ["All"] + editor_list)

with col2:
    client_list = ["All"] + clients_df["client_name"].tolist()
    client = st.selectbox("Client", client_list)

with col3:
    work = st.selectbox(
        "Work Type",
        ["All", "Reel", "Story Creative", "YouTube Video"]
    )

with col4:
    fy = st.selectbox("Financial Year", fy_list)

with col5:
    month_list = get_month_list(fy)
    month_select = st.selectbox("Month", month_list)

# =========================
# APPLY FILTERS
# =========================

if tasks_df.empty:
    st.info("No tasks found.")
    st.stop()

df = tasks_df.copy()

if editor != "All":
    df = df[df["editor"] == editor]

if client != "All":
    df = df[df["client_name"] == client]

if work != "All":
    df = df[df["work_type"] == work]

# Month filter (MMM-YYYY format)
df = df[df["month"] == month_select]

if df.empty:
    st.warning("No tasks for selected filters.")
    st.stop()

# =========================
# DISPLAY TASKS
# =========================

for index, row in df.iterrows():

    st.markdown('<div class="task-card">', unsafe_allow_html=True)

    st.write(f"**Client:** {row['client_name']}")
    st.write(f"**Work:** {row['work_type']}")
    st.write(f"**Editor:** {row['editor']}")
    st.write(f"**Month:** {row['month']}")
    st.write(f"**Status:** {row['status']}")

    # Pending Task
    if row["status"] == "Pending":

        url = st.text_input(
            "Paste Video URL",
            value=row["video_url"],
            key=row["task_id"]
        )

        if st.button("Mark Completed", key=f"complete{row['task_id']}"):

            url_clean = str(url).strip()

            # 🚨 1. EMPTY CHECK
            if not url_clean:
                st.error("⚠️ Please paste Video URL before marking as completed")

            else:
                # ✅ Normalize input
                normalized_input = normalize_url(url_clean)

                # 🔄 Load latest data
                latest_data = load_data()
                latest_tasks_df = latest_data["tasks"]

                existing_urls = latest_tasks_df[
                    latest_tasks_df["video_url"].notna()
                ].copy()

                # 🚨 Exclude current row
                existing_urls = existing_urls[
                    existing_urls["task_id"] != row["task_id"]
                ]

                # ✅ Normalize existing URLs
                existing_urls["video_url_norm"] = existing_urls["video_url"].apply(normalize_url)

                # 🚨 FINAL DUPLICATE CHECK
                if existing_urls["video_url_norm"].eq(normalized_input).any():

                    dup_row = existing_urls[
                        existing_urls["video_url_norm"] == normalized_input
                    ].iloc[0]

                    st.error(
                        f"⚠️ This video is already used for {dup_row['client_name']} - {dup_row['month']}"
                    )

                else:
                    data = row.to_dict()

                    data["video_url"] = url_clean
                    data["status"] = "Completed"
                    data["completed_date"] = str(datetime.today().date())

                    data.pop("task_id", None)

                    update_row("Work_Assignments", "task_id", row["task_id"], data)

                    st.cache_data.clear()
                    st.session_state.pop("app_data", None)
                    st.success("Task marked as Completed")
                    st.rerun()

    # Completed Task
    else:

        st.success("Completed")

        if st.button("Reopen Task", key=f"reopen{row['task_id']}"):

            data = row.to_dict()

            data["status"] = "Pending"
            data["completed_date"] = ""
            data["video_url"] = ""

            data.pop("task_id", None)

            update_row("Work_Assignments", "task_id", row["task_id"], data)
            
            st.cache_data.clear()
            st.session_state.pop("app_data", None)
            st.success("Task Reopened")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
