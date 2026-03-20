import streamlit as st
import pandas as pd
from datetime import datetime
from services.data_loader import load_data

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(layout="wide")

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

/* Header */
thead tr th{
    background:#0d47a1 !important;
    color:white !important;
    font-weight:700 !important;
}

/* Alternate rows */
tbody tr:nth-child(even){
    background:#e3f2fd;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

.page-title{
    font-size:34px;
    font-weight:700;
    margin-bottom:25px;
}

/* Table Header */
thead tr th{
    background:#0d47a1 !important;
    color:white !important;
    font-weight:700 !important;
}

/* Alternate rows */
tbody tr:nth-child(even){
    background:#e3f2fd;
}

tbody tr:nth-child(odd){
    background:white;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">📊 Client Dashboard</div>', unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================

data = load_data()

clients_df = data["clients"]
tasks_df = data["tasks"]

if clients_df.empty:
    st.warning("No clients available.")
    st.stop()

if tasks_df.empty:
    st.warning("No tasks available.")
    st.stop()

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

fy_list = [current_fy]

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

col1, col2, col3 = st.columns(3)

with col1:
    client_list = clients_df["client_name"].tolist()
    client = st.selectbox(
        "Client",
        ["Select Client"] + client_list
    )

    if client == "Select Client":
        st.stop()

with col2:
    fy = st.selectbox("Financial Year", fy_list)

with col3:
    month_list = ["All"] + get_month_list(fy)
    month = st.selectbox("Month", month_list, index=0)

# =========================
# APPLY FILTER
# =========================

client_tasks = tasks_df[
    tasks_df["client_name"] == client
]

if month != "All":
    client_tasks = client_tasks[
        client_tasks["month"] == month
    ]

if client_tasks.empty:
    st.info("No work assigned for selected period.")
    st.stop()


import re

package_string = clients_df.loc[
    clients_df["client_name"] == client,
    "package_details"
].values[0]

package = {}

for item in package_string.split(","):
    key, value = item.split(":")
    package[key.strip()] = int(re.sub("[^0-9]", "", value))
    
# =========================
# SUMMARY TABLE
# =========================

summary = (
    client_tasks.groupby("work_type")
    .agg(
        total=("task_id","count"),
        completed=("status", lambda x: (x=="Completed").sum())
    )
)

summary["pending"] = summary["total"] - summary["completed"]

summary = summary.reset_index()

st.markdown("### 📊 Work Progress")

for _, row in summary.iterrows():

    work = row["work_type"]
    total = row["total"]
    completed = row["completed"]

    progress = completed / total if total > 0 else 0

    st.write(f"**{work}**  ({completed} / {total})")

    st.progress(progress)

summary["package"] = summary["work_type"].map({
    "Reel": package.get("Reels",0),
    "Story Creative": package.get("Creatives",0),
    "YouTube Video": package.get("YouTube",0),
    "Meta Ads": package.get("MetaSpend",0),
})

st.markdown("""
<style>

/* Table full width */
table {
    width:100%;
    border-collapse:collapse;
    font-size:15px;
}

/* Header style */
thead tr th{
    background:#0d47a1;
    color:white;
    font-weight:700;
    padding:10px;
    text-align:left;
}

/* Cell padding */
td{
    padding:10px;
}

/* Alternate rows */
tbody tr:nth-child(even){
    background:#e3f2fd;
}

tbody tr:nth-child(odd){
    background:white;
}

</style>
""", unsafe_allow_html=True)

# =========================
# DISPLAY TABLE
# =========================

st.markdown('<div class="table-container">', unsafe_allow_html=True)

st.markdown(
    summary.to_html(index=False),
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("### 📦 Package vs Delivered")

for _, row in summary.iterrows():

    work = row["work_type"]
    completed = row["completed"]
    package_total = row["package"]

    if package_total == 0:
        continue

    progress = completed / package_total

    st.write(f"**{work}** ({completed} / {package_total})")

    st.progress(progress)