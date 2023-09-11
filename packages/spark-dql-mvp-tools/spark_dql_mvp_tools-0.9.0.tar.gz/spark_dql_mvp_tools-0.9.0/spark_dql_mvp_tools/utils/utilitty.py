def extract_only_parenthesis(format):
    import re
    _number = re.findall(r'\(.*?\)', format)
    if len(_number) > 0:
        res = str(_number[0])
        res = res.replace("(", "").replace(")", "").strip()
    else:
        res = ""
    return res


def extract_only_column_text(columns):
    import re
    new_col = str(columns).lower()
    _text = re.findall(r'([a-zA-Z ]+)', new_col)
    if len(_text) > 0:
        res = _text[0]
    else:
        res = ""
    return res
