from typing import Union


def parse_string(str_: str) -> Union[int, float, bool, str]:
    str_ = str_.strip()

    if str_.isnumeric():
        return int(str_)

    try:
        return float(str_)
    except ValueError:
        pass

    if str_.lower() in ['true', 'false']:
        return True if str_.lower() == 'true' else False

    return str_
