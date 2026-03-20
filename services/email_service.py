# path: services/email_service.py

import smtplib
from email.message import EmailMessage


EMAIL = "sumit.signaasat@gmail.com"


def send_invoice_email(to_email, invoice_no, amount, pdf_file):

    msg = EmailMessage()

    msg["Subject"] = f"Invoice {invoice_no} - Signaasat LLP"
    msg["From"] = EMAIL
    msg["To"] = to_email

    msg.set_content(
f"""
Subject: Payment Reminder - {invoice_no}

Dear Client,

This is a friendly reminder that payment for invoice {invoice_no}
amounting to ₹{amount} is still pending.

Kindly arrange payment.

Regards
Signaasat LLP
"""
)

    with open(pdf_file,"rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=pdf_file
        )

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as smtp:

        smtp.login(EMAIL,"asctyutdedmbeiyi")

        smtp.send_message(msg)
