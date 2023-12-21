import datetime

def convert_date(dict: dict):
    for k, v in dict.items():
        if isinstance(v, datetime.date):
            dict[k] = v.isoformat()
    return dict