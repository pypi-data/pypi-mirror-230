import re
import datetime

import brandpy


class FormattedDateTime:

    def __init__(self, in_date_str, in_hour_int, in_minutes_int, in_seconds_int):
        self.year = 2023
        self.month = 1
        self.day = 1
        if type(in_date_str) is str and len(in_date_str) > 0:
            if re.fullmatch("^[0-9][0-9][0-9][0-9]_[0-9][0-9]_[0-9][0-9]", in_date_str):
                self.year = int(in_date_str[0:4])
                self.month = int(in_date_str[5:7])
                self.day = int(in_date_str[8:10])
            else:
                raise Exception("in_date_str does not match the correct formatting", in_date_str)
        self.hour = int(in_hour_int)
        self.minutes = int(in_minutes_int)
        self.seconds = int(in_seconds_int)
        self.datetime_object = datetime.datetime(self.year, self.month, self.day, self.hour, self.minutes, self.seconds,
                                                 tzinfo=datetime.timezone.utc)

    def get_regular(self):
        return str(self.datetime_object)

    def get_file_name_format(self):
        return self.datetime_object.strftime("%Y_%m_%d_%H_%M_%S")

    def get_bw_format(self):
        return brandpy.BWAPIHelper.datetime_to_str(self.datetime_object)

    def __repr__(self):
        return self.get_regular()

    def __str__(self):
        return self.get_regular()
