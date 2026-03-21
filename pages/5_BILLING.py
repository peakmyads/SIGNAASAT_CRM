import streamlit as st
import pandas as pd
from datetime import datetime, date
from services.db_service import append_row, update_row
from services.data_loader import load_data
from services.invoice_service import generate_invoice_pdf, generate_invoice_number
from services.email_service import send_invoice_email

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Billing & Invoices")

# =========================
# LOAD CLIENT DATA
# =========================

data = load_data()
clients_df = data["clients"]

if clients_df.empty:
    st.warning("No clients available.")
    st.stop()

# =========================
# CLIENT FILTER
# =========================

client_list = clients_df["client_name"].tolist()

client = st.selectbox(
    "Client",
    ["Select Client"] + client_list
)

if client == "Select Client":
    st.stop()

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
# MONTH LIST (APR-MAR)
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


month_list = get_month_list(fy)

invoice_month = st.selectbox(
    "Invoice For Month",
    month_list
)

# =========================
# PACKAGE AMOUNT
# =========================

package_amount = int(clients_df.loc[
    clients_df["client_name"] == client,
    "monthly_fee"
].values[0])

st.markdown("### 📦 Package Amount")
st.info(f"₹ {package_amount}")

# =========================
# OTHER CHARGES
# =========================

st.markdown("### ➕ Other Charges")

col1, col2 = st.columns([3,1])

with col1:
    other_desc = st.text_input("Description")

with col2:
    other_amount = st.number_input(
        "Amount",
        min_value=0,
        step=100
    )

# =========================
# TOTAL INVOICE AMOUNT
# =========================

total_amount = package_amount + other_amount

st.markdown("### 💵 Total Invoice Amount")

st.success(f"₹ {total_amount}")

# =========================
# INVOICE NUMBER
# =========================

invoice_no = generate_invoice_number()

pdf = None

modify = False

st.write(f"Invoice No: **{invoice_no}**")

# =========================
# CLIENT EMAIL
# =========================

client_email = clients_df.loc[
    clients_df["client_name"] == client,
    "email"
].values[0]

st.write(f"Client Email: **{client_email}**")

billing_df = data["billing"]

existing_invoice = billing_df[
    (billing_df["client_name"] == client) &
    (billing_df["month"] == invoice_month)
]

if not existing_invoice.empty:

    st.warning("⚠ Invoice already exists for this Client and Month")

    invoice_no = existing_invoice.iloc[0]["invoice_no"]
    old_amount = existing_invoice.iloc[0]["amount"]
    
    pdf = generate_invoice_pdf(
        invoice_no,
        client,
        invoice_month,
        total_amount
    )
    
    st.info(f"Existing Invoice: {invoice_no} | Amount: ₹{old_amount}")
    
    modify = st.button("Modify Invoice")

    if modify:

        update_row(
            "Billing",              # table
            "invoice_no",           # WHERE column
            invoice_no,             # WHERE value
            {"amount": int(total_amount)}   # data to update
        )

        st.session_state.pop("app_data", None)

        st.success("Invoice Updated Successfully")

        st.rerun()
# =========================
# GENERATE INVOICE
# =========================

if existing_invoice.empty:

    if st.button("Generate Invoice"):

        invoice_no = generate_invoice_number()

        data = {
            "invoice_no": str(invoice_no),
            "client_name": str(client),
            "month": str(invoice_month),
            "amount": int(total_amount),
            "invoice_date": str(date.today()),
            "payment_status": "Pending",
            "payment_date": ""
        }

        append_row("Billing", data)

        st.session_state.pop("app_data", None)

        pdf = generate_invoice_pdf(
            invoice_no,
            client,
            invoice_month,
            total_amount
        )
        st.success(f"Invoice Generated: {invoice_no}")

# =========================
# DOWNLOAD + MODIFY + SEND
# =========================

if pdf is not None:

    with open(pdf, "rb") as f:

        st.download_button(
            "Download Invoice PDF",
            f,
            file_name=f"{invoice_no}.pdf"
        )

    if st.button("Send Invoice PDF"):

        send_invoice_email(
            client_email,
            invoice_no,
            total_amount,
            pdf
        )

        st.success("Invoice sent to client email.")
