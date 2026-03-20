# path: services/invoice_service.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from services.db_service import get_all


def get_financial_year():
    today = datetime.today()
    year = today.year

    if today.month < 4:
        start = year - 1
        end = year
    else:
        start = year
        end = year + 1

    return f"{str(start)[-2:]}-{str(end)[-2:]}"


def generate_invoice_number():

    billing_df = get_all("Billing")
    fy = get_financial_year()

    if billing_df.empty:
        return f"SIG/{fy}/001"

    count = len(billing_df) + 1
    number = str(count).zfill(3)

    return f"SIG/{fy}/{number}"


# path: services/invoice_service.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_invoice_pdf(invoice_no, client, amount, month):

    filename = f"{invoice_no.replace('/','_')}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)

    # LOGO
    try:
        c.drawImage("logo.png", 50, 780, width=80, height=50)
    except:
        pass

    # COMPANY DETAILS
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, 800, "Signaasat LLP")

    c.setFont("Helvetica", 10)

    c.drawString(150, 780, "Office No. 1003 10th Floor")
    c.drawString(150, 765, "Geras Imperium Alpha")
    c.drawString(150, 750, "Vadgaon Sheri Pune 411014")
    c.drawString(150, 735, "GSTIN: 27ABOCS1745A1ZE")

    # INVOICE HEADER
    c.setFont("Helvetica-Bold", 14)
    c.drawString(420, 800, "INVOICE")

    c.setFont("Helvetica", 10)

    c.drawString(420, 780, f"Invoice No: {invoice_no}")
    c.drawString(420, 765, f"Date: {datetime.today().date()}")

    # CLIENT DETAILS
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 700, "Bill To:")

    c.setFont("Helvetica", 11)
    c.drawString(50, 680, client)

    # SERVICE TABLE
    c.setFont("Helvetica-Bold", 11)

    c.drawString(50, 640, "Description")
    c.drawString(450, 640, "Amount")

    c.line(50, 635, 550, 635)

    c.setFont("Helvetica", 11)

    c.drawString(50, 610, f"Digital Marketing Services - {month}")
    c.drawString(450, 610, f"₹ {amount}")

    c.line(50, 600, 550, 600)

    # TOTAL
    c.setFont("Helvetica-Bold", 12)

    c.drawString(350, 560, "Total")
    c.drawString(450, 560, f"₹ {amount}")

    # BANK DETAILS
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 500, "Bank Details")

    c.setFont("Helvetica", 10)

    c.drawString(50, 480, "Bank: HDFC Bank")
    c.drawString(50, 465, "A/c No: 50200110589223")
    c.drawString(50, 450, "IFSC: HDFC0000103")

    c.save()

    return filename

