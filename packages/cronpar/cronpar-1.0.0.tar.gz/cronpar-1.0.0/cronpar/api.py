import calendar
from datetime import datetime

TODAY = datetime.today()
DEFAULT_OUTCOME = {
    "minute": list(range(0, 60)),
    "hour": list(range(0, 24)),
    "day of month": list(range(1, calendar.monthrange(TODAY.year, TODAY.month)[1] + 1)),
    "month": list(range(1, 13)),
    "day of week": list(range(1, 8)),
    "command": "unknown",
}


def _parse_str(value: str, _type: str) -> list[int]:
    res = []
    _limit = DEFAULT_OUTCOME[_type][-1]

    if "/" in value:
        interval = int(value.split("/")[1])
        if _type in {"minute", "hour"}:
            res.append(0)
        member = interval
        while member <= _limit:
            res.append(member)
            member += interval
    elif "," in value:
        res.extend([int(m) for m in value.split(",")])
    elif "-" in value:
        start, end = value.split("-")
        assert int(end) <= _limit, f"{_type} cannot be greater than {_limit}"
        res.extend(range(int(start), int(end) + 1))
    else:
        if value.isnumeric():
            res.append(int(value))
        else:
            raise ValueError(f"{_type} value {value} not understood.")

    return res


def explain(cmd: list[str]):
    res = DEFAULT_OUTCOME.copy()
    cron_types = list(res.keys())
    command = ""

    try:
        for idx, c in enumerate(cmd):
            if idx < 5:
                if c != "*":
                    res[cron_types[idx]] = _parse_str(c, cron_types[idx])
            else:
                if not command:
                    command += c
                else:
                    command += " " + c
    except ValueError as ex:
        raise ValueError(ex)

    res["command"] = command

    for i, (name, expr) in enumerate(res.items()):
        if i < 5:
            print(f"{name:<14}{' '.join([str(x) for x in expr])}")
        else:
            print(f"{name:<14}{expr}")
