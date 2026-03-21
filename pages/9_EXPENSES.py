import streamlit as st
import pandas as pd
from datetime import date, datetime
from services.db_service import append_row
from services.data_loader import load_data

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Expense Tracking")

tab1, tab2 = st.tabs(["Add Expense", "Expense List"])


# =========================
# BUTTON STYLE
# =========================

st.markdown("""
<style>

div.stButton > button {
    background-color:#5A67D8;
    color:white;
    border-radius:8px;
    padding:10px 20px;
    font-weight:600;
}

div.stButton > button:hover {
    background-color:#434190;
}

</style>
""", unsafe_allow_html=True)


# =========================
# ADD EXPENSE TAB
# =========================

with tab1:

    st.subheader("Add Expense")

    col1, col2 = st.columns(2)

    with col1:
        expense_date = st.date_input("Date", date.today())

    with col2:
        category = st.selectbox(
            "Cost Centre",
            [
                "Staff Salary",
                "Office Rent",
                "Office Electricity",
                "Contractor – Video Recording",
                "Travelling",
                "Staff Welfare",
                "Subscriptions",
                "Personal",
                "Other"
            ]
        )

    col3, col4 = st.columns(2)

    with col3:
        amount = st.number_input("Amount", min_value=0, step=500)

    with col4:
        description = st.text_input("Description *")

    if st.button("Add Expense"):

        if description.strip() == "":
            st.error("Description is mandatory")
            st.stop()

        data = {
            "expense_id": str(expense_date) + category,
            "date": str(expense_date),
            "category": category,
            "amount": int(amount),
            "description": description
        }

        append_row("Expenses", data)

        st.session_state.pop("app_data", None)
        st.success("Expense added successfully!")
        st.rerun()



# =========================
# EXPENSE LIST TAB
# =========================

with tab2:

    st.subheader("Expense List")

    data = load_data()
    df = data["expenses"]

    if df.empty:
        st.info("No expenses recorded.")
        st.stop()


    # =========================
    # DATE CONVERSION
    # =========================

    df["date"] = pd.to_datetime(df["date"])


    # =========================
    # FINANCIAL YEAR LOGIC
    # =========================

    today = datetime.today()

    if today.month >= 4:
        fy_start = today.year
    else:
        fy_start = today.year - 1

    current_fy = f"{fy_start}-{str(fy_start+1)[2:]}"
    next_fy = f"{fy_start+1}-{str(fy_start+2)[2:]}"

    fy_list = [current_fy]

    if today.month >= 4:
        fy_list.append(next_fy)

    fy = st.selectbox("Financial Year", fy_list)


    # =========================
    # MONTH LIST
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

        return [f"{m}-{y}" for m,y in months]


    month_list = ["All"] + get_month_list(fy)

    month = st.selectbox("Month", month_list, index=0)


    # =========================
    # FILTER DATA
    # =========================

    df["month"] = df["date"].dt.strftime("%b-%Y")

    if month != "All":
        df = df[df["month"] == month]


    # =========================
    # TABLE STYLING
    # =========================

    st.markdown("""
    <style>

    table {
        border-collapse: collapse;
        width: 100%;
    }

    thead tr th {
        background-color:#1E4E9E;
        color:white;
        font-weight:700;
        text-align:left;
        padding:10px;
    }

    tbody tr:nth-child(even) {
        background-color:#E8F0FE;
    }

    tbody tr:nth-child(odd) {
        background-color:white;
    }

    tbody td {
        padding:8px;
    }

    </style>
    """, unsafe_allow_html=True)


    # =========================
    # CLEAN DATA
    # =========================

    df = df.drop(columns=["expense_id"], errors="ignore")

    # Format Date
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d-%b-%Y")

    # Rename Columns
    df.columns = [col.replace("_", " ").title() for col in df.columns]


    # =========================
    # TABLE STYLE
    # =========================

    table_html = """
    <style>

    .expense-table {
        border-collapse: collapse;
        width: 100%;
        font-family: sans-serif;
    }

    .expense-table th {
        background-color: #1E4E9E;
        color: white;
        font-weight: bold;
        padding: 10px;
        text-align: left;
    }

    .expense-table td {
        padding: 8px;
    }

    .expense-table tr:nth-child(even) {
        background-color: #E8F0FE;
    }

    .expense-table tr:nth-child(odd) {
        background-color: white;
    }

    </style>
    """


    # =========================
    # BUILD TABLE
    # =========================

    table_html += "<table class='expense-table'>"

    # Header
    table_html += "<tr>"
    for col in df.columns:
        table_html += f"<th>{col}</th>"
    table_html += "</tr>"

    # Rows
    for _, row in df.iterrows():

        table_html += "<tr>"

        for val in row:
            table_html += f"<td>{val}</td>"

        table_html += "</tr>"

    table_html += "</table>"
    
    st.markdown(table_html, unsafe_allow_html=True)
