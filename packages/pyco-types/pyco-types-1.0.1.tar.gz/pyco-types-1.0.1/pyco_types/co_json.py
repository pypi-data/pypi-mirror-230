import json
import uuid

from pprint import pformat
from datetime import datetime
from logging import root as logger


def pformat_any(data, depth=2, width=80, indent=2, **kwargs):
    return " :: ".join([str(type(data)), pformat(data, indent=indent, width=width, depth=depth)])


class CustomJSONEncoder(json.JSONEncoder):
    """
    default support datetime.datetime and uuid.UUID
    enable convert object by custom `http exception`
    usually:
        "to_json":  Common Class
        "to_dict":  Custom Model
        "as_dict"： SQLAlchemy Rows
        "get_json": json response
        "__html__": jinja templates

    """
    _jsonify_methods = [
        "jsonify",
        "to_json",
        "get_json",  # json response
        "to_dict",
        "as_dict",  # SQLAlchemy Rows
        "__html__",  # jinja templates
        "_asdict",  ## collections, namedtuple 
        "toJson",
        "getJson",  # json response
        "toDict",
        "asDict",  # SQLAlchemy Rows
    ]

    ##； @_jsonify_strict: 如果设置为 True, 则尝试使用原生 JSON, 可能会异常
    ##； @_jsonify_strict: 如果设置为 False, 则不管怎样都能返回 序列化的结果（不一定符合预期）
    _jsonify_strict = False
    _pformat_depth = 2
    _datetime_fmt = '%Y-%m-%d %H:%M:%S'

    # _datetime_fmt = '%Y-%m-%d %H:%M:%S.%f'

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(self._datetime_fmt)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        else:
            for k in self._jsonify_methods:
                fn = getattr(obj, k, None)
                if callable(fn):
                    return fn()
                elif isinstance(fn, (str, int, float, dict)):
                    return fn

            if self._jsonify_strict:
                m = json.JSONEncoder.default(self, obj)
            else:
                m = pformat_any(obj, depth=self._pformat_depth)
                logger.error(f"[JsonEncoded???] {m}")
            return m


def json_format(data, indent=2, cls=CustomJSONEncoder, **kwargs):
    if isinstance(data, str):
        try:
            obj = json.loads(data)
            return json_format(obj, indent=indent, cls=cls, **kwargs)
        except:
            return data
    else:
        return json.dumps(data, indent=indent, cls=cls, **kwargs)


def parse_json(data):
    if isinstance(data, str):
        try:
            obj = json.loads(data)
            return obj
        except:
            return data
    else:
        return data
