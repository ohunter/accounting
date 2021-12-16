from datetime import timedelta


def fmt_duration(dt: timedelta) -> str:
    hours, rem = divmod(dt.total_seconds(), 3600)
    minutes = rem // 60

    return f"{int(hours):>02}:{int(minutes):02}"


def fmt_float(cur: float) -> str:
    return f"{cur:.2f}"
