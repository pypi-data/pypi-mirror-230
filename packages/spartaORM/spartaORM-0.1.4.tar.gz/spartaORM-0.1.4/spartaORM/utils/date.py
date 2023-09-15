from datetime import datetime


def str_to_date(date_str: str, format: str = "%Y-%m-%d"):
    """
    Converts a string to a date
    """
    return datetime.strptime(date_str, format)
