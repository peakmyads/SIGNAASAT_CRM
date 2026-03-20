import streamlit as st
import plotly.express as px
import pandas as pd
from services.db_service import get_all
from services.data_loader import load_data

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

st.markdown("""
<style>

.dashboard-title{
    font-size:28px;
    font-weight:700;
    margin-bottom:10px;
}

.kpi-card{
    padding:18px;
    border-radius:12px;
    color:white;
    text-align:center;
    font-weight:600;
}

.clients {background-color:#4CAF50;}
.completed {background-color:#2196F3;}
.pending {background-color:#FF9800;}
.revenue {background-color:#673AB7;}
.cost {background-color:#F44336;}
.profit {background-color:#009688;}

.kpi-number{
    font-size:28px;
    font-weight:700;
}

</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

st.title("🏠 Signaasat Dashboard")

# -------------------------
# Load Data
# -------------------------

data = load_data()

clients_df = data["clients"]
tasks_df = data["tasks"]
billing_df = data["billing"]
expenses_df = data["expenses"]

# -------------------------
# Metrics Calculations
# -------------------------

total_clients = len(clients_df)

total_tasks = len(tasks_df)

completed_tasks = (
    len(tasks_df[tasks_df["status"] == "Completed"])
    if not tasks_df.empty else 0
)

pending_tasks = total_tasks - completed_tasks

total_revenue = billing_df["amount"].sum() if not billing_df.empty else 0

total_cost = expenses_df["amount"].sum() if not expenses_df.empty else 0

profit = total_revenue - total_cost

profit_percentage = (
    (profit / total_revenue) * 100
    if total_revenue > 0 else 0
)

# -------------------------
# KPI Cards
# -------------------------

st.markdown('<div class="dashboard-title">Business Overview</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="kpi-card clients">
        Clients<br>
        <div class="kpi-number">{total_clients}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card completed">
        Completed Work<br>
        <div class="kpi-number">{completed_tasks}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card pending">
        Pending Work<br>
        <div class="kpi-number">{pending_tasks}</div>
    </div>
    """, unsafe_allow_html=True)
    
st.divider()

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(f"""
    <div class="kpi-card revenue">
        Revenue<br>
        <div class="kpi-number">₹{total_revenue:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card cost">
        Cost<br>
        <div class="kpi-number">₹{total_cost:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="kpi-card profit">
        Profit %<br>
        <div class="kpi-number">{profit_percentage:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# -------------------------
# Charts Section
# -------------------------

chart1, chart2 = st.columns(2)

with chart1:

    st.markdown("### Work Status")

    if not tasks_df.empty:

        status_count = tasks_df["status"].value_counts().reset_index()
        status_count.columns = ["Status", "Count"]

        fig = px.pie(
            status_count,
            names="Status",
            values="Count",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No work data available")


with chart2:

    st.markdown("### Revenue vs Cost")

    df = pd.DataFrame({
        "Type": ["Revenue", "Cost"],
        "Amount": [total_revenue, total_cost]
    })

    fig = px.bar(
        df,
        x="Type",
        y="Amount",
        text="Amount",
        color="Type"
    )

    st.plotly_chart(fig, use_container_width=True)