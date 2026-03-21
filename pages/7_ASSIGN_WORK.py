# path: pages/3_assign_work.py

import streamlit as st
import uuid
from datetime import date
import pandas as pd
from services.db_service import append_row
from services.data_loader import load_data
from services.whatsapp_service import send_whatsapp
from services.workload_service import get_least_busy_editor

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# UI STYLE
# =========================

st.markdown("""
<style>

.page-title{
    font-size:32px;
    font-weight:700;
    margin-bottom:20px;
}

/* Page card */
.card{
    background:white;
    padding:25px;
    border-radius:12px;
    box-shadow:0 4px 15px rgba(0,0,0,0.08);
}

/* Button */
div.stButton > button{
    background:linear-gradient(90deg,#6a5cff,#8f7bff);
    color:white;
    border:none;
    padding:10px 22px;
    border-radius:8px;
    font-weight:600;
}

div.stButton > button:hover{
    background:linear-gradient(90deg,#5a4bff,#7b68ff);
}

</style>
""", unsafe_allow_html=True)


# =========================
# PAGE TITLE
# =========================

st.title("📝 Assign Work")

# =========================
# LOAD CLIENTS
# =========================

data = load_data()
clients_df = data["clients"]

if clients_df.empty:
    st.warning("No clients available. Please add a client first.")
    st.stop()

client_list = ["Select Client"] + list(clients_df["client_name"].unique())

client = st.selectbox(
        "Select Client",
        client_list,
        index=0
    )
    
# =========================
# WORK TYPE
# =========================

work_types = [
    "Reel",
    "Story Creative",
    "YouTube Video",
    "Meta Ads",
    "Google Ads"
]

work_type = st.selectbox("Work Type", work_types)


data = load_data()
editors_df = data.get("editors", pd.DataFrame())

# =========================
# AUTO ASSIGN OPTION
# =========================

auto_assign = st.checkbox("Auto Assign Editor")

if auto_assign:
    editor = get_least_busy_editor()
    st.info(f"Assigned Editor: {editor}")

else:

    if editors_df.empty:
        editor_list = []
    else:
        editor_list = editors_df["editor_name"].tolist()

    editor = st.multiselect(
        "Assign Editor(s)",
        editor_list
    )

# =========================
# ADD NEW EDITOR
# =========================

with st.expander("➕ Add New Editor"):

    new_editor_name = st.text_input("Editor Name")

    new_editor_phone = st.text_input("Phone")

    # Auto add +91 if missing
    if new_editor_phone and not new_editor_phone.startswith("+"):
        new_editor_phone = "+91" + new_editor_phone

    if st.session_state.get("editor_saved"):
        st.success("✅ Editor saved successfully")
        st.session_state["editor_saved"] = False
    
    if st.button("Save Editor"):

        if new_editor_name.strip() == "":
            st.warning("Please enter editor name")
            st.stop()

        if not new_editor_phone.startswith("+") or len(new_editor_phone) < 12:
            st.error("Invalid phone number. Use format: +91XXXXXXXXXX")
            st.stop()

        # 🔥 LOAD EXISTING EDITORS
        existing_editors = load_data().get("editors", pd.DataFrame())

        new_name = new_editor_name.strip().lower()

        if not existing_editors.empty:

            existing_names = (
                existing_editors["editor_name"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            # ❌ EXACT DUPLICATE BLOCK
            if new_name in existing_names.values:
                st.error("❌ Editor already exists!")
                st.stop()

            # ⚠️ SIMILAR NAME WARNING
            similar = existing_editors[
                existing_editors["editor_name"]
                .str.lower()
                .str.contains(new_name[:3], na=False)
            ]

            if not similar.empty:
                st.warning("⚠️ Similar editor names found:")
                st.dataframe(similar[["editor_name"]])

                confirm = st.checkbox("I confirm this is a different editor")

                if not confirm:
                    st.stop()

        # ✅ SAVE EDITOR
        new_editor = {
            "editor_id": str(uuid.uuid4())[:6],
            "editor_name": new_editor_name.title(),
            "phone": new_editor_phone
        }

        append_row("Editors", new_editor)

        # 🔥 CLEAR CACHE
        st.cache_data.clear()

        # 🔥 SUCCESS MESSAGE BEFORE RERUN
        st.success("✅ Editor added successfully!")

        # 🔥 PREVENT DOUBLE CLICK
        st.session_state["editor_saved"] = True

        st.rerun()

# =========================
# TASK INPUT BASED ON WORK TYPE
# =========================
def get_month_list_for_current_fy():

    today = date.today()

    if today.month >= 4:
        start_year = today.year
    else:
        start_year = today.year - 1

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

today = date.today()
current_month = today.strftime("%b-%Y")

month_list = get_month_list_for_current_fy()

# Find index of current month
default_index = month_list.index(current_month) if current_month in month_list else 0

month = st.selectbox(
    "Month",
    month_list,
    index=default_index
)

# For Content Tasks
if work_type in ["Reel", "Story Creative", "YouTube Video"]:

    count = st.number_input(
        "Number of Tasks",
        min_value=1,
        step=1
    )

    budget = None

# For Ads Work
elif work_type in ["Meta Ads", "Google Ads"]:

    budget = st.number_input(
        "Ad Budget Spent (₹)",
        min_value=0,
        step=100
    )

    count = 1

def get_package_limit(package_str, work_type):

    reels = creatives = youtube = 0

    try:
        pkg = package_str.replace("\n","").replace("\\n","")
        parts = [p.strip() for p in pkg.split(",") if p.strip()]

        data = {}
        for p in parts:
            if ":" in p:
                k,v = p.split(":")
                data[k.strip().lower()] = int(v.strip())

        reels = data.get("reels",0)
        creatives = data.get("creatives",0)
        youtube = data.get("youtube",0)

    except:
        pass

    if work_type == "Reel":
        return reels
    elif work_type == "Story Creative":
        return creatives
    elif work_type == "YouTube Video":
        return youtube
    else:
        return None

# =========================
# LOAD TASK DATA (ADD HERE)
# =========================

tasks_df = load_data().get("tasks", pd.DataFrame())

if not tasks_df.empty:
    tasks_df.columns = tasks_df.columns.str.strip().str.lower()

confirm_create = st.checkbox(
    f"⚠️ Confirm creating {count} task(s) for {month} - {client}"
)

if st.button("Create Tasks", type="primary"):

    # =========================
    # BASIC VALIDATION
    # =========================

    if client == "Select Client":
        st.error("Please select a client")
        st.stop()

    if not editor:
        st.error("Please select at least one editor")
        st.stop()

    if not confirm_create:
        st.warning("Please confirm before creating tasks")
        st.stop()

    # =========================
    # PACKAGE VALIDATION
    # =========================

    client_row = clients_df[
        clients_df["client_name"] == client
    ]

    if not client_row.empty:

        package_str = client_row.iloc[0]["package_details"]

        package_limit = get_package_limit(package_str, work_type)

        if package_limit is not None:

            required_cols = ["client_name", "month", "work_type"]

            if tasks_df.empty or not all(col in tasks_df.columns for col in required_cols):
                existing_count = 0
            else:
                tasks_df["work_type"] = tasks_df["work_type"].astype(str).str.strip().str.lower()

                work_type_clean = work_type.strip().lower()

                # Normalize DB columns
                tasks_df["client_name"] = tasks_df["client_name"].astype(str).str.strip().str.lower()
                tasks_df["month"] = tasks_df["month"].astype(str).str.strip().str.lower()
                tasks_df["work_type"] = tasks_df["work_type"].astype(str).str.strip().str.lower()

                # Normalize UI inputs
                client_clean = client.strip().lower()
                month_clean = month.strip().lower()
                work_type_clean = work_type.strip().lower()
                
                existing_tasks = tasks_df[
                    (tasks_df["client_name"] == client_clean) &
                    (tasks_df["month"] == month_clean) &
                    (tasks_df["work_type"] == work_type_clean)
                ]

                existing_count = len(existing_tasks)

            new_requested = count

            if existing_count >= package_limit:
                st.error(
                    f"⚠️ All {work_type} tasks already assigned "
                    f"({existing_count}/{package_limit})"
                )
                st.stop()

            if existing_count + new_requested > package_limit:

                remaining = package_limit - existing_count

                st.error(
                    f"⚠️ Only {remaining} {work_type} task(s) remaining.\n"
                    f"You are trying to create {new_requested}"
                )
                st.stop()

    # =========================
    # CREATE TASKS
    # =========================

    editors_cycle = editor if isinstance(editor, list) else [editor]

    for i in range(count):

        ed = editors_cycle[i % len(editors_cycle)]   # round-robin

        task_id = str(uuid.uuid4())[:8]

        data = {
            "task_id": task_id,
            "client_id": "",
            "client_name": client,
            "work_type": work_type,
            "editor": ed,
            "status": "Pending",
            "month": month,
            "video_url": "",
            "ad_budget": budget if budget else "",
            "created_date": str(today),
            "completed_date": ""
        }

        append_row("Work_Assignments", data)

    st.success(f"{count} tasks created successfully!")

    # =========================
    # WHATSAPP
    # =========================

    try:
        for ed in editor:

            editor_phone = editors_df.loc[
                editors_df["editor_name"] == ed,
                "phone"
            ]

            if editor_phone.empty:
                continue

            phone = editor_phone.values[0]

            send_whatsapp(phone, client, work_type, month)

        st.success("WhatsApp sent ✅")

    except Exception as e:
        st.warning(f"WhatsApp failed: {e}")

    st.cache_data.clear()
    st.rerun()
    
