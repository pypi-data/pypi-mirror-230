import re
from ._common import CommonException


def alphanumeric(s: str, sep='_'):
    """
    # refer: https://stackoverflow.com/a/12985459/6705684
    # Note that \W is equivalent to [^a-zA-Z0-9_] only in Python 2.x.
    # In Python 3.x, \W+ is equivalent to [^a-zA-Z0-9_] only if re.ASCII / re.A flag is used.
    >>> alphanumeric('h^&ell`.,|o w]{+orld')
    'h_ell_o_w_orld'
    """
    return re.sub('[^0-9a-zA-Z]+', sep, s.strip())


def simple_case(s: str):
    """
    # better pathname/filename, accept only alpha numbers and [_-.]
    >>>simple_case("xxasdfIS _asdkf ks. asfx - dkasx"))
    'xxasdfIS_asdkfks.asfx-dkasx'
    >>>simple_case("xxasdfIS ÓÔÔLIasdf_asdkf中文ks. asfx - dkasx"))
    'xxasdfISLIasdf_asdkfks.asfx-dkasx'
    """
    return re.sub(r"[^0-9a-zA-Z_\-\.]+", '', s)


def snake_case(s: str):
    """
    # refer: https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    # smarter than ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')
    >>> snake_case('getHTTPResponseCode')
    'get_http_response_code'
    >>> snake_case('get2HTTPResponseCode')
    'get2_http_response_code'
    >>> snake_case('get2HTTPResponse123Code')
    'get2_http_response123_code'
    >>> snake_case('HTTPResponseCode')
    'http_response_code'
    >>> snake_case('HTTPResponseCodeXYZ')
    'http_response_code_xyz'
    """
    s = alphanumeric(s, '_')
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    return a.sub(r'_\1', s).lower()


def camel_case(s: str):
    """
    # suggest to preprocess $s with $simple_case or $alphanumeric
    >>> camel_case("Some rise ^升起^. Some fade ª••º.")
    'SomeRise ^升起^. SomeFade ª••º.'
    >>> camel_case("Some live to die another day.")
    'SomeLiveToDieAnotherDay.'
    >>> camel_case("I’ll live to die another day.")
    'I’llLiveToDieAnotherDay.'
    """
    return re.sub(r"[\-_\.\s]([a-z])", lambda mo: mo.group(1).upper(), s)


def title_case(s: str):
    """
    # refer: https://docs.python.org/3/library/stdtypes.html#str.title
    >>> title_case("they're bill's friends.")
    "They're Bill's Friends."
    """
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo: mo.group(0).capitalize(), s)


class CoRegexPatten(object):
    def __init__(self, patten="", note="", key=None, zh=""):
        self.patten = patten
        self.note = note
        self.key = key
        self.zh = zh

    def to_dict(self):
        return vars(self)

    def match(self, value: str, silent=True, key=None):
        m = re.match(self.patten, value)
        if not m and not silent:
            k = key or self.key or self.zh or ''
            msg = '[PattenUnmatched] {}'.format(k)
            raise CommonException(msg, errno=40005, note=self.note)
        return m


class RegexPattenMeta(type):
    def __getattribute__(self, item):
        m = super().__getattribute__(item)
        if isinstance(m, CoRegexPatten) and m.key is None:
            m.key = item
        return m


class RegexMap(metaclass=RegexPattenMeta):
    version = CoRegexPatten(
        patten="\d+(?:\.\d+)*",
        note="由数字和小数点组成，eg: 1.2.4",
        zh="版本号",
    )

    datestr = CoRegexPatten(
        patten="^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$",
        note="DateString:  yyyy-mm-dd 或 yyyy-m-d",
        zh="日期",
    )

    field_key = CoRegexPatten(
        patten='^([a-zA-Z_]+)([a-zA-Z0-9_\.-]){2,63}$',
        note="首字符为字母, 长度不超过64，由字母数字组成的字符串（不允许空格, 符号仅支持_-.）",
        zh='索引键',
    )

    hex_str = CoRegexPatten(
        patten="^0[xX][0-9a-fA-F]+$",
        note="前缀为 0x 或 0X 的十六进制，不定长, eg: 0xA(16)",
        zh="十六进制的数值",
    )

    hex_str6 = CoRegexPatten(
        patten="^0[xX][0-9a-fA-F]{6}+$",
        note="前缀为 0x 或 0X 的十六进制, 限制长度必须为6，如果不足则补零，eg: 0x00000A",
        zh="6位十六进制",
    )

    otc_str = CoRegexPatten(
        patten="^0[oO][0-7]+$",
        note="前缀为 0x 或 0X 的八进制, 不定长, eg: 0o10(8)",
        zh="八进制的数值",
    )

    bin_str = CoRegexPatten(
        patten="^0[bB][0-1]+$",
        note="前缀为 0x 或 0X 的二进制, 不定长, eg:0b10(2)",
        zh="二进制的数值",
    )

    var_name = CoRegexPatten(
        patten="^[A-Za-z_][A-Za-z0-9_]*$",
        note="首字符为字母, 仅由字母数字和下划线组成的字符串",
        zh='变量名',
    )

    var_type = CoRegexPatten(
        patten="^<class '([a-zA-Z]+)'>$",
        note='输入值为type(value), eg: "<class \'int\'>"',
        zh='值类型',
    )

    def __getattribute__(self, item):
        m = super().__getattribute__(item)
        if isinstance(m, CoRegexPatten) and m.key is None:
            m.key = item
        return m

    @classmethod
    def to_dict(cls):
        d = {}
        for k, m in vars(cls).items():
            if isinstance(m, CoRegexPatten):
                d[k] = m.to_dict()
        return d
