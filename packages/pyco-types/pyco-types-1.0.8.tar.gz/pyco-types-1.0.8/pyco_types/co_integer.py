import math
import string

from ._convert_meta import Converter

STATIC_BASE_MAP = {
    "0b": 2,
    "0B": 2,
    "0o": 8,
    "0O": 8,
    "0x": 16,
    "0X": 16,
    "#|": 36,  ##;36进制自定义的前缀:[0-10]+[a/A-z/Z] 不区分大小写
    "#&": 62,  ##;62进制自定义的前缀:[0-10]+[az]+[AZ] 区分大小写
}

##: 统一先大写后小写，和 ascii 顺序一致 
STATIC_BASE_STRING = string.digits + string.ascii_uppercase + string.ascii_lowercase
STATIC_BASE_POSVAL = dict((c, v) for v, c in enumerate(STATIC_BASE_STRING))


def int2base(value, base):
    """
    @base: int: [2, 62], base <=2 and base >=62
    @return: str
    """
    return ''.join(
        [STATIC_BASE_STRING[(value // base ** i) % base]
         for i in range(int(math.log(value, base)), -1, -1)]
    )


# def base2int(string: str, base: int):
#     ## 等同于: int(string, base)
#     num = 0
#     if base <= 36:
#         string = string.upper()
#     for char in string:
#         num = num * base + STATIC_BASE_POSVAL[char]
#     return num



class FloatFmt(Converter, float):
    _type = float

    @classmethod
    def convert(cls, v, **kwargs):
        ## float("-1e1")
        ## -10.0
        return float(v)


class BoolIntFmt(Converter, int):
    _type = int

    ## 设定：把bool值转为三种状态：明确的 True(1), False(0), Unset(-1)
    default_null = -1
    default_values_map = {
        "": default_null,
        "null": default_null,
        "none": default_null,
        "false": 0,
        "0": 0,
        "no": 0,
        "n": 0,
        "f": 0,
    }

    @classmethod
    def convert(cls, value, **kwargs):
        if isinstance(value, str):
            v = value.strip().lower()
            return cls.default_values_map.get(v, 1)
        elif value is None:
            return cls.default_null
        elif isinstance(value, int):
            return value
        else:
            vb = bool(value)
            v = 1 if vb else 0
            return v


class IntegerFmt(Converter, int):
    _type = int

    default_base = 10
    base_prefix = {
        '10': "",
        "2": "0b",
        "8": "0o",
        "16": "0x",
        "36": "#|",
        "62": "#&",
    }

    @classmethod
    def stringify(cls, value: int, base=default_base, zfill_width=-1):
        ## STATIC_BASE_RANGE = [2, 62]
        if base == 10:
            t = str(value)
            # if __width > 0:
            return t.zfill(zfill_width)

        if base < 2 or base > 62:
            raise ValueError(f"int2base(value={value}, base={base}), $base should in (2,62)")

        v = int2base(value, base)
        b = int2base(base, base)
        prefix = cls.base_prefix.get(str(base), f"{b}?")
        return f'{prefix}{v.zfill(zfill_width)}'


    @classmethod
    def convert(cls, value, default_value=0, default_base=10):
        if isinstance(value, (int, float)):
            return int(value)
        elif value is True:
            return 1
        elif value is False:
            return 0
        elif value:
            if isinstance(value, str):
                p = value[:2]
                if p.isdigit():
                    return int(value, default_base)
                else:
                    base = STATIC_BASE_MAP.get(p, default_base)
                    p2 = value[2:]
                    v = int(p2, base)
                return v
            else:
                v = int(value)
                return v
        else:
            return default_value


parse_int = IntegerFmt.convert
parse_bool = BoolIntFmt.convert