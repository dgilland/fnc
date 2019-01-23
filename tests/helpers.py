class AttrObject(object):
    def __init__(self, **attrs):
        for attr, value in attrs.items():
            setattr(self, attr, value)


class KeysGetItemObject(object):
    def __init__(self, mapping):
        self.mapping = mapping

    def keys(self):
        return self.mapping.keys()

    def __getitem__(self, item):
        return self.mapping[item]


class IterMappingObject(object):
    def __init__(self, mapping):
        self.mapping = mapping

    def __iter__(self):
        return iter(self.mapping.items())
