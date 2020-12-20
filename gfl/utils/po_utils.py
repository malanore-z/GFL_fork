__all__ = [
    "PlainObject"
]


def is_primary_type(tp):
    return tp in [type(None), bool, int, float, str]


def is_container_type(tp):
    return tp in [tuple, list, set, dict]


class Field(object):

    def __init__(self, name, tp):
        super(Field, self).__init__()
        self.name = name
        self.tp = tp if isinstance(tp, list) or isinstance(tp, tuple) else (tp,)
        self.top_type = None
        self.main_type = None
        self.verify()

    def value(self, obj):
        return getattr(obj, self.name, None)

    def is_primay(self):
        return is_primary_type(self.top_type)

    def is_container(self):
        return is_container_type(self.top_type)

    def verify(self):
        if len(self.tp) < 1 or None in self.tp:
            raise ValueError("Field defined error: illegal type defination of %s" % self.name)
        self.top_type = self.tp[0]
        for t in self.tp[:-1]:
            if not is_container_type(t):
                raise ValueError("Field defined error: illegal type defination of %s" % self.name)
        self.main_type = self.tp[-1]
        if not is_primary_type(self.main_type) and not issubclass(self.main_type, PlainObject):
            raise ValueError("Field defined error: illegal type defination of %s" % self.name)


class PlainObject(object):

    def __init__(self, **kwargs):
        super(PlainObject, self).__init__()
        args = kwargs
        self.__assign_args(type(self), args)
        if len(args) > 0:
            raise ValueError("%s not exists." % (args.popitem()[0]))

    def __assign_args(self, cls, args):
        if cls == PlainObject:
            return
        if len(cls.__bases__) > 1:
            raise TypeError("multi inherit is not supported.")
        self.__assign_args(cls.__bases__[0], args)
        for k, f in reflect_metadata(cls).items():
            val = args.pop(k, None)
            setattr(self, k, val)

    def to_dict(self):
        return po_to_dict(type(self), self)

    def from_dict(self, dt: dict):
        return po_from_dict(type(self), self, dt)


metadata_cache = {}


def reflect_metadata(cls):
    global metadata_cache
    if cls in metadata_cache:
        return metadata_cache[cls]
    fields = {}
    for k, v in cls.__dict__.items():
        if not k.startswith("_") and not callable(getattr(cls, k)):
            fields[k] = Field(k, v)
    metadata_cache[cls] = fields
    return fields


def container_to_dict(tp, obj):
    if is_primary_type(tp[0]):
        return obj
    if is_container_type(tp[0]):
        if tp[0] == dict:
            ret = {}
            for k, v in obj.items():
                ret[k] = container_to_dict(tp[1:], v)
        else:
            ret = []
            for v in obj:
                ret.append(container_to_dict(tp[1:], v))
        return ret
    return obj.to_dict()


def container_from_dict(tp, dt):
    if is_primary_type(tp[0]):
        return dt
    if is_container_type(tp[0]):
        if tp[0] == dict:
            ret = {}
            for k, v in dt.items():
                ret[k] = container_from_dict(tp[1:], v)
        else:
            ret = []
            for v in dt:
                ret.append(container_from_dict(tp[1:], v))
            ret = tp[0](ret)
        return ret
    return tp[0]().from_dict(dt)


def po_to_dict(cls, obj: PlainObject):
    if cls == PlainObject:
        return {}

    super_cls = cls.__base__
    ret = po_to_dict(super_cls, obj)

    for k, f in reflect_metadata(cls).items():
        val = getattr(obj, k, None)
        if val is None:
            ret[k] = None
            continue
        if f.is_primay():
            ret[f.name] = val
        elif f.is_container():
            ret[f.name] = container_to_dict(f.tp, val)
        else:
            ret[f.name] = val.to_dict()
    return ret


def po_from_dict(cls, obj, dt):
    if cls == PlainObject:
        return obj

    super_cls = cls.__base__
    obj = po_from_dict(super_cls, obj, dt)

    for k, f in reflect_metadata(cls).items():
        val = dt.get(k)
        if val is None:
            continue
        if f.is_primay():
            setattr(obj, f.name, val)
        elif f.is_container():
            setattr(obj, f.name, container_from_dict(f.tp, val))
        else:
            setattr(obj, f.name, f.main_type().from_dict(val))

    return obj
