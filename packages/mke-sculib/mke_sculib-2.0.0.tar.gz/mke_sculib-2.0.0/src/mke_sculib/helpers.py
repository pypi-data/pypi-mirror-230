import dateutil.parser, datetime, time, re


def get_utcnow():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

def make_zulustr(dtobj, remove_ms = True):
    utc = dtobj.replace(tzinfo=datetime.timezone.utc)
    if remove_ms:
        utc = utc.replace(microsecond=0)
    return utc.isoformat().replace('+00:00','') + 'Z'

def mk_dtz(dtobj=None, remove_ms = True):
    if dtobj is None:
        dtobj = get_utcnow()
    return make_zulustr(dtobj, remove_ms).replace('T',' ').replace('Z',' ')

def match_zulutime(s):
    if s is None: return None

    s = s.strip()
    if '.' in s and re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{1,6}Z', s) is not None:
        return s
    elif 'T' in s and re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', s) is not None:
        return s
    elif re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}Z', s) is not None:
        return s
    else:
        return None


def parse_zulutime(s):
    try:
        if re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}Z', s) is not None:
            s = s[:-1] + 'T00:00:00Z'
        return dateutil.parser.isoparse(s).replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return None