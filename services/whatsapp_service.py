from twilio.rest import Client

ACCOUNT_SID = "C0d21857844791044ee5c7a1feb5df464"
AUTH_TOKEN = "fd52d403396a82fa3818e04ea47a19e5"

FROM_WHATSAPP = "whatsapp:+14155238886"


def send_whatsapp(phone, client_name, work_type, month):

    if not phone:
        raise Exception("Editor phone number not found")

    if not phone.startswith("whatsapp:"):
        phone = "whatsapp:" + phone

    dashboard_link = "http://localhost:8501/Client_Dashboard"

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