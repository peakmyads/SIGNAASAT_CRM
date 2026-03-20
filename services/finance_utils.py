# path: services/finance_utils.py

from datetime import datetime


def get_financial_year(date):

    year = date.year

    if date.month < 4:
        start = year - 1
        end = year
    else:
        start = year
        end = year + 1

    return f"{start}-{str(end)[-2:]}"


def generate_fy_list():

    current = datetime.today()

    fy = get_financial_year(current)

    start_year = int(fy.split("-")[0])

    fy_list = []

    for i in range(5):
        y = start_year - i
        fy_list.append(f"{y}-{str(y+1)[-2:]}")

    return fy_list
