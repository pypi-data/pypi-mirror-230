from dateutil.relativedelta import relativedelta

import re


def parse_period(period: str) -> relativedelta:
    pattern = r"(\d+)([dmy])"

    if result := re.match(pattern, period):
        value, unit = result.groups()

        match unit:
            case "d":
                return relativedelta(days=int(value))
            case "m":
                return relativedelta(months=int(value))
            case "y":
                return relativedelta(years=int(value))
    else:
        raise ValueError(f"Invalid period string: {period}")
