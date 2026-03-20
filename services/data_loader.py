import streamlit as st
from services.db_service import get_all


@st.cache_data(ttl=60)
def load_data():

    clients = get_all("Clients")
    editors = get_all("Editors")
    tasks = get_all("Work_Assignments")
    billing = get_all("Billing")
    expenses = get_all("Expenses")
    social = get_all("Social_Insights")

    return {
        "clients": clients,
        "editors": editors,
        "billing": billing,
        "tasks": tasks,
        "expenses": expenses,
        "social": social
    }