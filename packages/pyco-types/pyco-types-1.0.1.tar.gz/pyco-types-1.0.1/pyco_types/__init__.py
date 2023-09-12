# -*- coding: utf-8 -*-
try:
    from ._version import version as __version__
    from ._convert_meta import Converter, ConverterMeta
    from ._common import CommonException
    from .co_datetime import DateFmt
    from .co_regex import RegexMap, CoRegexPatten

except ImportError:
    __version__ = 'unknown'
