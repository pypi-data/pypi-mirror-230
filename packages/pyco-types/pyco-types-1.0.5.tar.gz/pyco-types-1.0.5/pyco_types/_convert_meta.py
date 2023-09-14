class ConverterMeta(type):
    _co_registered_class = []

    def __init__(rcls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        rcls._co_metatype = ConverterMeta
        _type = getattr(rcls, "_type", None)
        if _type is None:
            rcls._type = rcls
        ConverterMeta._co_registered_class.append(rcls)


    @property
    def _list_cousin_class(cls):
        return cls._co_registered_class

    def __instancecheck__(self, instance):
        return isinstance(instance, self._type)


class Converter(metaclass=ConverterMeta):
    """
    实现效果如下: a = Converter(1)
    assert isinstance(a, Converter)
    assert isinstance(a, str)
    """
    _type = str

    @property
    def __class__(self):
        return self._type

    @classmethod
    def convert(cls, v, **kwargs):
        ### 只需要重构此函数
        return cls._type(v)

    @classmethod
    def fetch_dict(cls, type_instance: _type):
        to_dict = getattr(type_instance, "to_dict", None)
        if callable(to_dict):
            return to_dict()
        return vars(type_instance)

    @classmethod
    def stringify(cls, type_instance: _type):
        return str(type_instance)

    def __new__(cls, v=None, **kwargs):
        self = cls.convert(v, **kwargs)
        return self

    @classmethod
    def _adapt_dict(cls, origin_dict: dict, flex_dict: dict):
        ori_keys = origin_dict.keys()
        for k, v in flex_dict.items():
            if k in ori_keys:
                origin_dict[k] = v

    @classmethod
    def _check_updated_fields(cls, origin_dict: dict, flex_dict: dict):
        ori_keys = origin_dict.keys()
        res = {}
        for k, v in flex_dict.items():
            if k in ori_keys:
                if origin_dict[k] != v:
                    res[k] = v
        return res
