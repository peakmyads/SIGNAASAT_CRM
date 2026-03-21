# path: pages/2_clients.py

import streamlit as st
import json
import uuid
import pandas as pd
from datetime import date
from services.db_service import append_row
from services.data_loader import load_data

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM UI STYLE
# =========================

st.markdown("""
<style>

.page-title{
    font-size:32px;
    font-weight:700;
    margin-bottom:15px;
}

/* TAB BAR */
button[data-baseweb="tab"]{
    font-size:18px !important;
    font-weight:700 !important;
    padding:8px 18px !important;
    border-radius:8px 8px 0px 0px !important;
}

/* ACTIVE TAB */
button[data-baseweb="tab"][aria-selected="true"]{
    background-color:#6a5cff !important;
    color:white !important;
}

/* INACTIVE TAB */
button[data-baseweb="tab"][aria-selected="false"]{
    background-color:#f3f4f6 !important;
    color:#444 !important;
}

/* Button styling */
div.stButton > button{
    background: linear-gradient(90deg,#6a5cff,#8f7bff);
    color:white;
    border:none;
    border-radius:8px;
    padding:10px 24px;
    font-weight:600;
}

div.stButton > button:hover{
    background: linear-gradient(90deg,#5948ff,#7b68ff);
}

button[data-baseweb="tab"]{
    font-size:16px;
    font-weight:600;
}

.section-header{
    font-size:20px;
    font-weight:700;
    margin-bottom:15px;
}

/* FORM LABELS (Client Name, Phone, etc.) */
div[data-testid="stWidgetLabel"] label{
    font-size:20px !important;
    font-weight:800 !important;
    color:#1a1a1a !important;
}

/* INPUT BACKGROUND */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input{
    background-color:#e8f5e9 !important;
}

/* SELECT BOX */
.stSelectbox div[data-baseweb="select"]{
    background-color:#e8f5e9 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Make field labels bold and larger */
.stTextInput label,
.stSelectbox label,
.stTextArea label,
.stDateInput label,
.stNumberInput label{
    font-size:18px !important;
    font-weight:700 !important;
    color:#1a1a1a !important;
}

/* Light green background input boxes */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input{
    background-color:#e8f5e9 !important;
    border-radius:6px !important;
}

/* Dropdown styling */
.stSelectbox div[data-baseweb="select"]{
    background-color:#e8f5e9 !important;
}

/* Table header styling */
.custom-table thead tr{
    background-color:#0b3d91;
    color:white;
    font-weight:bold;
}

/* Alternate row color */
.custom-table tbody tr:nth-child(even){
    background-color:#e8f1ff;
}

/* Table styling */
.custom-table{
    border-collapse:collapse;
    width:100%;
}

.custom-table th, .custom-table td{
    padding:10px;
    border:1px solid #dcdcdc;
    text-align:left;
}

</style>
""", unsafe_allow_html=True)

# =========================
# PAGE TITLE
# =========================

st.markdown('<div class="page-title">👥 Client Management</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["➕ Add Client", "📋 Client List"])

# =====================================================
# ADD CLIENT
# =====================================================

with tab1:

    st.markdown('<div class="section-header">Client Onboarding</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        client_name = st.text_input("Client Name")

        client_type = st.selectbox(
            "Client Type",
            ["Doctor","Hospital"]
        )

        contact_person = st.text_input("Contact Person")

        phone = st.text_input("Phone")

        email = st.text_input("Email")

    with col2:

        address = st.text_area("Address")

        gstin = st.text_input(
            "GSTIN (15 digits max)",
            max_chars=15
        )

        start_date = st.date_input(
            "Start Date",
            date.today()
        )

        monthly_fee = st.number_input(
            "Monthly Fee (₹)",
            min_value=0
        )

    # =========================
    # PACKAGE DETAILS
    # =========================

    st.markdown('<div class="section-header">📦 Package Details</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        reels = st.number_input(
            "Reels Count",
            min_value=0,
            max_value=999999,
            step=1
        )

    with c2:
        creatives = st.number_input(
            "Story Creatives Count",
            min_value=0,
            max_value=999999,
            step=1
        )

    with c3:
        youtube = st.number_input(
            "YouTube Videos Count",
            min_value=0,
            max_value=999999,
            step=1
        )

    # =========================
    # AD BUDGET
    # =========================

    st.markdown('<div class="section-header">📢 Ad Budget</div>', unsafe_allow_html=True)

    c4, c5 = st.columns(2)

    with c4:
        meta_spend = st.number_input(
            "Meta Ad Spend (₹)",
            min_value=0,
            max_value=999999
        )

    with c5:
        google_spend = st.number_input(
            "Google Ad Spend (₹)",
            min_value=0,
            max_value=999999
        )

    # =========================
    # ADD CLIENT BUTTON
    # =========================

    existing_clients = load_data().get("clients", pd.DataFrame())
    
    if st.button("Add Client", key="add_client_btn"):

        if client_name.strip() == "":
            st.error("Client Name is required")
            st.stop()

        new_name = client_name.strip().lower()

        if not existing_clients.empty:

            existing_names = (
                existing_clients["client_name"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            # ❌ Exact duplicate check
            if new_name in existing_names.values:
                st.error("❌ Client already exists!")
                st.stop()

            # ⚠️ Similar name check
            similar = existing_clients[
                existing_clients["client_name"]
                .str.lower()
                .str.contains(new_name[:4], na=False)
            ]

            if not similar.empty:
                st.warning("⚠️ Similar client names found:")
                st.dataframe(similar[["client_name"]])

                confirm = st.checkbox("I confirm this is a different client")

                if not confirm:
                    st.stop()

        # ✅ Proceed if no issues
        client_id = str(uuid.uuid4())[:8]
        start_date_format = start_date.strftime("%d-%b-%Y")

        package = f"""
    Reels:{reels},
    Creatives:{creatives},
    YouTube:{youtube},
    MetaSpend:{meta_spend},
    GoogleSpend:{google_spend}
    """

        data = {
            "client_id": client_id,
            "client_name": client_name.title(),
            "client_type": client_type,
            "contact_person": contact_person.title(),
            "phone": phone,
            "email": email,
            "address": address,
            "gstin": gstin.upper(),
            "start_date": start_date_format,
            "monthly_fee": monthly_fee,
            "package_details": package,
            "created_at": str(date.today())
        }

        append_row("Clients", data)

        st.cache_data.clear()
        st.session_state.pop("app_data", None)

        st.success("✅ Client Added Successfully")
        st.rerun()

# =====================================================
# CLIENT LIST
# =====================================================

import json

def format_package(pkg):

    reels = creatives = youtube = meta = google = 0

    try:
        if isinstance(pkg, str):

            # Try JSON first
            try:
                data = json.loads(pkg)
            except:
                # fallback for old text format
                pkg = pkg.replace("\\n","").replace("\n","")
                parts = [p.strip() for p in pkg.split(",") if p.strip()]
                data = {}

                for p in parts:
                    if ":" in p:
                        k,v = p.split(":")
                        data[k.strip().lower()] = v.strip()

        else:
            data = pkg

        reels = data.get("reels",0)
        creatives = data.get("creatives",0)
        youtube = data.get("youtube",0)

        meta = data.get("meta_spend", data.get("metaspent",0))
        google = data.get("google_spend", data.get("googlespend",0))

    except:
        pass

    return f"Reels:{reels}, Creatives:{creatives}, YouTube:{youtube}, MetaSpend:₹{meta}, GoogleSpend:₹{google}"

with tab2:

    st.markdown('<div class="section-header">Client Directory</div>', unsafe_allow_html=True)

    data = load_data()
    df = data["clients"]
    df["package_details"] = df["package_details"].apply(format_package)

    if df.empty:

        st.info("No clients added yet.")

    else:

        df = df.copy()

        df.insert(0,"Sr No",range(1,len(df)+1))

        df.columns = (
            df.columns
            .str.replace("_"," ")
            .str.title()
        )

        styled_df = df.style.set_table_styles(
            [
                {
                    "selector":"th",
                    "props":[
                        ("background-color","#0b3d91"),
                        ("color","white"),
                        ("font-weight","bold")
                    ]
                }
            ]
        ).apply(
            lambda x: [
                "background-color:#e8f1ff" if i%2 else ""
                for i in range(len(x))
            ],
            axis=0
        )

        table_html = df.to_html(index=False, classes="custom-table")
        st.markdown(table_html, unsafe_allow_html=True)
