import dateutil.parser as dt_parser
import datetime as dt

def convert_date(date, format='%Y.%m.%d'):
    try:
        if isinstance(date, (str)):
            date = dt_parser.parse(date)
    except Exception as e:
        raise Exception('date:{}格式不能识别。' % date)

    return "date('{0}')".format(date.strftime(format))


def deconvert_date(date_str, format='%Y.%m.%d'):
    try:
        if isinstance(date_str, (str)):
            date = dt.datetime.strptime(date_str,"(date('{0}'))".format(format)).strftime('%Y-%m-%d')
    except Exception as e:
        raise Exception('date:{}格式不能识别。' % date_str)

    return date

def to_format(key, express, values):
    if express == 'in':
        values = ', '.join(
            map(lambda x: f"'{x}'" if isinstance(x, str) else f"{x}", values))
        return "{0} {1} [{2}]".format(key, express, values)
    else:
        values = values
        return "{0} {1} ({2})".format(key, express, values)