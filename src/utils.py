import re


def decade_from_date(date):
    if isinstance(date, str):
        match = re.search(r'(\d{4})', date)
        if match:
            year = int(match.group(1)) +1
            decade = (year // 10) * 10
            return f"{decade}s"
    elif hasattr(date, 'year'):
        year = date.year + 1
        decade = (year // 10) * 10
        return f"{decade}s"
    return ''

def clStr(MyStr):
    if MyStr == '' or MyStr is None:
        return ''
    retStr = re.sub(r'[^a-zA-Z0-9éèàç&êöë \-]', ' ', MyStr)
    retStr = retStr.replace('www', '').replace('webm', '').replace('slider', '').replace('youtube', '')
    #retStr = retStr.title()
    retStr = retStr.lower()
    return str(retStr)

