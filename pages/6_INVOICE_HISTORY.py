import streamlit as st
import pandas as pd
from datetime import datetime, date

from services.db_service import get_all, update_row
from services.data_loader import load_data
from services.invoice_service import generate_invoice_pdf
from services.email_service import send_invoice_email

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

st.set_page_config(layout="wide")

st.title("🧾 Invoice History")

data = load_data()

billing_df = data["billing"]
clients_df = data["clients"]

if billing_df.empty:
    st.info("No invoices found.")
    st.stop()


# =========================
# FILTERS
# =========================

st.markdown("### Filters")

col1, col2, col3, col4 = st.columns([2,2,2,1])

client_list = ["All"] + sorted(billing_df["client_name"].unique().tolist())

with col1:
    client_filter = st.selectbox("Client", client_list)

today = datetime.today()

if today.month >= 4:
    fy_start = today.year
else:
    fy_start = today.year - 1

current_fy = f"{fy_start}-{str(fy_start+1)[2:]}"
next_fy = f"{fy_start+1}-{str(fy_start+2)[2:]}"

fy_list = ["All", current_fy]

with col2:
    fy_filter = st.selectbox("Financial Year", fy_list)


def get_month_list(fy):

    if fy == "All":
        return ["All"]

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

    return ["All"] + [f"{m}-{y}" for m,y in months]


with col3:
    month_filter = st.selectbox("Month", get_month_list(fy_filter))


# REFRESH BUTTON
with col4:

    if st.button("🔄 Refresh"):

        st.session_state.pop("app_data", None)
        st.rerun()


# =========================
# APPLY FILTERS
# =========================

df = billing_df.copy()

if client_filter != "All":
    df = df[df["client_name"] == client_filter]

if month_filter != "All":
    df = df[df["month"] == month_filter]

search = st.text_input("🔎 Search Invoice / Client")

if search:
    df = df[
        df["client_name"].str.contains(search, case=False) |
        df["invoice_no"].str.contains(search, case=False)
    ]

# =========================
# DASHBOARD SUMMARY
# =========================

st.markdown("""
<style>

.metric-card{
    padding:22px;
    border-radius:14px;
    color:white;
    font-weight:500;
    margin-bottom:15px;
}

.metric-total{
    background:linear-gradient(135deg,#6a8cff,#4e5ef7);
}

.metric-paid{
    background:linear-gradient(135deg,#38b48b,#2d9e74);
}

.metric-pending{
    background:linear-gradient(135deg,#f59f00,#f08c00);
}

.metric-title{
    font-size:14px;
    opacity:0.9;
}

.metric-value{
    font-size:34px;
    font-weight:700;
}

</style>
""", unsafe_allow_html=True)


total_revenue = billing_df["amount"].sum()

paid_df = billing_df[billing_df["payment_status"] == "Paid"]
partial_df = billing_df[billing_df["payment_status"] == "Partial Paid"]

paid_amount = paid_df["amount"].sum()

pending_amount = billing_df["amount"].sum() - paid_amount


c1,c2,c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card metric-total">
        <div class="metric-title">💰 Total Billing</div>
        <div class="metric-value">₹ {total_revenue:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card metric-paid">
        <div class="metric-title">✅ Paid</div>
        <div class="metric-value">₹ {paid_amount:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card metric-pending">
        <div class="metric-title">⏳ Pending</div>
        <div class="metric-value">₹ {pending_amount:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.markdown("---")

h1, h2, h3, h4, h5, h6, h7 = st.columns([2,1.5,2,1.5,1.5,1.5,3])

h1.markdown("**Client**")
h2.markdown("**Month**")
h3.markdown("**Invoice**")
h4.markdown("**Amount**")
h5.markdown("**Remaining**")
h6.markdown("**Status**")
h7.markdown("**Actions**")

st.markdown("---")


# =========================
# INVOICE LIST
# =========================

billing_df = get_all("Billing")

for i, row in df.iterrows():

    invoice_amount = int(row["amount"])

    payment_amount = row.get("payment_amount", 0)

    if payment_amount == "" or pd.isna(payment_amount):
        payment_amount = 0

    remaining = invoice_amount - int(payment_amount)

    col1, col2, col3, col4, col5, col6, col7 = st.columns([2,1.5,2,1.5,1.5,1.5,3])

    with col1:
        st.write(row["client_name"])

    with col2:
        st.write(row["month"])

    with col3:
        st.write(row["invoice_no"])

    with col4:
        st.write(f"₹ {invoice_amount}")

    with col5:
        st.write(f"₹ {remaining}")

    with col6:

        invoice_amount = int(row["amount"])

        payment_amount = row.get("payment_amount", 0)

        if payment_amount == "" or pd.isna(payment_amount):
            payment_amount = 0

        payment_amount = int(payment_amount)

        # AUTO STATUS CALCULATION
        if payment_amount == 0:
            status = "Pending"
        elif payment_amount < invoice_amount:
            status = "Partial Paid"
        else:
            status = "Paid"


        if status == "Paid":
            st.success("✅ Paid")

        elif status == "Partial Paid":
            st.info("🟦 Partial")

        else:
            st.warning("⏳ Pending")

    with col7:

        pdf = generate_invoice_pdf(
            row["invoice_no"],
            row["client_name"],
            row["month"],
            row["amount"]
        )

        b1, b2, b3 = st.columns(3)

        # DOWNLOAD
        b1, b2, b3 = st.columns(3)

        with b1:
            with open(pdf, "rb") as f:
                st.download_button(
                    "📄 PDF",
                    f,
                    file_name=pdf,
                    key=f"download{i}",
                    use_container_width=True
                )

        with b2:
            if st.button("✉️ Send", key=f"send{i}", use_container_width=True):

                email_rows = clients_df.loc[
                    clients_df["client_name"] == row["client_name"],
                    "email"
                ]

                if email_rows.empty:
                    st.error("Client email not found")

                else:

                    send_invoice_email(
                        email_rows.values[0],
                        row["invoice_no"],
                        row["amount"],
                        pdf
                    )

                    st.success("Invoice sent")

        # PAYMENT BUTTON
        with b3:

            if row["payment_status"] == "Paid":

                if st.button("✏️ Edit", key=f"edit{i}", use_container_width=True):

                    st.session_state[f"payment_form_{i}"] = True

            else:

                if st.button("💰 Record", key=f"pay{i}", type="primary", use_container_width=True):

                    st.session_state[f"payment_form_{i}"] = True


    # =========================
    # PAYMENT FORM
    # =========================

    if st.session_state.get(f"payment_form_{i}", False):

        with st.expander("Record Payment Details", expanded=True):

            # ✅ FIX 1: Existing Amount
            existing_amount = row.get("payment_amount")

            if pd.isna(existing_amount) or existing_amount == "":
                existing_amount = row["amount"]

            existing_amount = int(existing_amount)

            # ✅ FIX 2: Existing Date (MISSING BEFORE)
            existing_date = row.get("payment_date")

            if pd.isna(existing_date) or existing_date == "":
                existing_date = date.today()
            else:
                existing_date = pd.to_datetime(existing_date)

            # ✅ FIX 3: Existing Mode
            existing_mode = row.get("payment_mode")

            valid_modes = ["Bank", "Cash", "Personal Bank", "Other"]

            if pd.isna(existing_mode) or existing_mode not in valid_modes:
                existing_mode = "Bank"

            # =========================
            # INPUT FIELDS
            # =========================

            p1, p2, p3 = st.columns(3)

            with p1:
                amount = int(st.number_input(
                    "Amount Received",
                    value=existing_amount,
                    key=f"amt{i}"
                ))

            with p2:
                pay_date = st.date_input(
                    "Date Received",
                    value=existing_date,   # ✅ FIXED (no pd.to_datetime here)
                    key=f"date{i}"
                )

            with p3:
                mode = st.selectbox(
                    "Mode",
                    valid_modes,
                    index=valid_modes.index(existing_mode),
                    key=f"mode{i}"
                )

            if st.button("✅ Save Payment", key=f"save{i}", type="primary", use_container_width=True):
                
                paid_amount = int(st.session_state.get(f"amt{i}", 0))

                if paid_amount == 0:
                    status = "Pending"

                elif paid_amount < invoice_amount:
                    status = "Partial Paid"

                else:
                    status = "Paid"

                update_row(
                    "Billing",
                    "invoice_no",
                    row["invoice_no"],
                    {
                        "payment_status": status,
                        "payment_date": str(pay_date),
                        "payment_mode": mode,
                        "payment_amount": amount
                    }
                )
                
                st.cache_data.clear()

                st.success("Payment Updated")

                st.session_state[f"payment_form_{i}"] = False

                st.session_state.pop("app_data", None)

                st.rerun()