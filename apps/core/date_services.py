from datetime import datetime


def dateformat_ymd(date):
    return datetime.strftime(date, "%Y-%m-%d")