import datetime as DT

import time

from ._convert_meta import Converter


class DateFmt(Converter, DT.datetime):
    """
    注意: (Converter,DT.datetime) 顺序不可调换, 否则需要重构 __new__, 实现效果如下

    a = DateFmt()
    print(type(a))                  ##;<class 'datetime.datetime'>
    print(isinstance(a,DT.datetime))  ##;True
    print(isinstance(a, DateFmt))   ##;True
    print(issubclass(DateFmt, Converter))   ##;True
    print(isinstance(DateFmt, ConverterMeta))   ##;True
    print(issubclass(DateFmt, ConverterMeta))   ##;False
    
    """
    # _types = (datetime, None.__class__)
    _type = DT.datetime
    ## 东八区的 time.timezone = -28800, 使用系统时区, 不要使用默认编码
    utc_offset = DT.timedelta(seconds=-time.timezone)
    ignore_microsecond = True


    @classmethod
    def jsonify(cls, value: DT.datetime, fmt=None, ignore_microsecond=True):
        s = sum([value.hour, value.minute, value.second])
        if fmt is None:
            if s == 0:
                fmt = "%Y-%m-%d"
            elif value.microsecond == 0 or ignore_microsecond:
                fmt = "%Y-%m-%d %H:%M:%S"
            else:
                fmt = "%Y-%m-%d %H:%M:%S.%f"
        return value.strftime(fmt)


    @classmethod
    def fetch_dict(cls, self: _type):
        return dict(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            microsecond=self.microsecond,
            tzinfo=self.tzinfo
        )


    @classmethod
    def range_years(cls, year=None, offset=1, **kwargs):
        default_kws = dict(month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        cls._adapt_dict(default_kws, kwargs)
        if year is None:
            year = DT.datetime.now().year
        this_year = DT.datetime(year, **default_kws)
        next_year = DT.datetime(year + offset, **default_kws)
        return (this_year, next_year)

    @classmethod
    def range_months(cls, month=None, year=None, offset=1, **kwargs):
        default_kws = dict(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        cls._adapt_dict(default_kws, kwargs)
        if year is None:
            year = DT.datetime.now().year
        if month is None:
            month = DT.datetime.now().month
        m2 = month + offset
        year2 = year + (m2) // 12
        month2 = m2 % 12 + 1

        this_month = DT.datetime(year, month, **default_kws)
        next_month = DT.datetime(year2, month2, **default_kws)
        return (this_month, next_month)

    @classmethod
    def range_days(cls, day=None, month=None, year=None, offset=1, **kwargs):
        default_kws = dict(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        cls._adapt_dict(default_kws, kwargs)
        if day is None:
            day = DT.datetime.now().day
        if year is None:
            year = DT.datetime.now().year
        if month is None:
            month = DT.datetime.now().month

        this_day = DT.datetime(month, year, day, **default_kws)
        next_day = this_day + DT.timedelta(days=offset)
        return (this_day, next_day)

    @classmethod
    def initial(cls, offset_days=0, **kwargs):
        now = DT.datetime.now()
        default_kws = dict(
            year=now.year, month=now.month, day=now.day,
            hour=0, minute=0, second=0, microsecond=0,
            tzinfo=None
        )
        cls._adapt_dict(default_kws, kwargs)
        ## date = now.replace(**default_kws) ==> now.date()
        d = DT.datetime(**default_kws)
        if offset_days != 0:
            dt = DT.timedelta(days=offset_days)
            d += dt
        return d


    @classmethod
    def convert(cls, date_value=None, offset_days=0, **kwargs):
        if not date_value:
            return cls.initial(offset_days=offset_days, **kwargs)
        elif isinstance(date_value, DT.datetime):
            return date_value
        elif isinstance(date_value, DT.date):
            return DT.datetime(date_value.year, date_value.month, date_value.day)
        elif isinstance(date_value, str):
            from dateutil.parser import parse as parse_date
            return parse_date(date_value)
        elif isinstance(date_value, (int, float)):
            return DT.datetime.fromtimestamp(date_value)
        elif isinstance(date_value, tuple):
            return DT.datetime(*date_value)
        else:
            raise ValueError(f"invalid {cls._type.__name__}<{type(date_value)}: {date_value}>")

    def __new__(cls, v=None, offset_days=0, **kwargs):
        self = cls.convert(v, offset_days=offset_days)
        return self
