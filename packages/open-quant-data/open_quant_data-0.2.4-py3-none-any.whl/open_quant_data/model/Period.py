import enum


class Period(enum.Enum):
    DAILY = 1
    MONTHLY = 2
    YEARLY = 3
    MINUTE_1 = 4
    MINUTE_10 = 5
    HOUR = 6
    TICK = 7
