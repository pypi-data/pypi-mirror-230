import re


def cutoff_unit(string):
    regex = r'[-+]?\d*\.\d+|\d+'
    value = re.search(regex, string)
    if value:
        return value.group()
    else:
        return None
