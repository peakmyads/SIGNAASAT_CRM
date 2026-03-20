# path: pages/8_management_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from services.data_loader import load_data
from services.finance_utils import get_financial_year, generate_fy_list
from datetime import datetime

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

st.title("📈 Management Dashboard")

# LOAD DATA FIRST
data = load_data()

billing_df = data["billing"]
expenses_df = data["expenses"]
tasks_df = data["tasks"]

fy_list = generate_fy_list()

selected_fy = st.selectbox("Financial Year", fy_list)


# FILTER BILLING BY FY
if not billing_df.empty:

    billing_df["invoice_date"] = pd.to_datetime(billing_df["invoice_date"])

    billing_df["FY"] = billing_df["invoice_date"].apply(get_financial_year)

    billing_df = billing_df[billing_df["FY"] == selected_fy]


# FILTER EXPENSES BY FY
if not expenses_df.empty:

    expenses_df["date"] = pd.to_datetime(expenses_df["date"])

    expenses_df["FY"] = expenses_df["date"].apply(get_financial_year)

    expenses_df = expenses_df[expenses_df["FY"] == selected_fy]

# ----------------------
# Revenue
# ----------------------

if billing_df.empty:
    total_revenue = 0
else:
    total_revenue = billing_df["amount"].sum()

# ----------------------
# Expenses
# ----------------------

if expenses_df.empty:
    total_expenses = 0
else:
    total_expenses = expenses_df["amount"].sum()

profit = total_revenue - total_expenses

# ----------------------
# Pending Work
# ----------------------

if tasks_df.empty:
    pending_work = 0
else:
    pending_work = len(tasks_df[tasks_df["status"] == "Pending"])


# ----------------------
# KPI Cards
# ----------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", f"₹{total_revenue}")
col2.metric("Expenses", f"₹{total_expenses}")
col3.metric("Profit", f"₹{profit}")
col4.metric("Pending Work", pending_work)


# ----------------------
# Revenue Chart
# ----------------------

st.markdown("### Revenue by Client")

if not billing_df.empty:

    fig = px.bar(
        billing_df,
        x="client_name",
        y="amount",
        title="Client Revenue"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No revenue data yet.")


# ----------------------
# Expense Chart
# ----------------------

st.markdown("### Expenses by Category")

if not expenses_df.empty:

    fig = px.pie(
        expenses_df,
        names="category",
        values="amount"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No expense data yet.")
    
billing_all = billing_df.copy()

if not billing_all.empty:

    billing_all["invoice_date"] = pd.to_datetime(billing_all["invoice_date"])

    overdue = billing_all[
        (billing_all["payment_status"] == "Pending") &
        ((datetime.today() - billing_all["invoice_date"]).dt.days > 30)
    ]

    st.markdown("### Overdue Invoices")

    if overdue.empty:
        st.success("No overdue invoices")
    else:
        st.dataframe(overdue)

