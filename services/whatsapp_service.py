import os
import streamlit as st
from twilio.rest import Client

try:
    ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
except:
    ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

FROM_WHATSAPP = "whatsapp:+14155238886"


def send_whatsapp(phone, client_name, work_type, month):

    if not phone:
        raise Exception("Editor phone number not found")

    if not phone.startswith("whatsapp:"):
        phone = "whatsapp:" + phone

    dashboard_link = "https://signaasatcrm-xu4ftvrp2dwgbq7pns3gkq.streamlit.app/EDITOR_TASKS"

    message_body = f"""
🎬 *New Task Assigned*

👤 Client: {client_name}
🎯 Work: {work_type}
📅 Month: {month}

👉 View Task:
{dashboard_link}

Please update status in CRM.
"""

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    client.messages.create(
        body=message_body,
        from_=FROM_WHATSAPP,
        to=phone
    )
