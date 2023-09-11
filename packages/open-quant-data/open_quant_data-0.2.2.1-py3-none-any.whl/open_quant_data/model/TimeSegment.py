import datetime


class TimeSegment:
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime):
        self.start_time = start_time
        self.end_time = end_time
