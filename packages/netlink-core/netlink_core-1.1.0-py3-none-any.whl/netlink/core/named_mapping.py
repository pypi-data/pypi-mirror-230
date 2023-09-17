from .mapping import Mapping


class NamedMapping(Mapping):
    __slots__ = ("_data", '_normalized')

    def __init__(self, **kwargs):
        """
        Mapping providing access via attribute name

        If attribute name contains '_' and is not found, search is repeated with '_' replaced by '-'

        If not found search is repeated case-insensitive

        :param kwargs:
        """
        self._data = {k: v for k, v in kwargs.items()}
        self._normalized = {}
        for k in self._data:
            self._normalized[k.lower()] = self._data[k]

    def __search(self, item):
        if item not in self._data:
            if '_' in item:
                return self.__search(item.replace('_', '-'))
            elif not item.islower():
                return self.__search(item.lower())
            else:
                raise AttributeError
        return self._data[item]

    def __getattr__(self, item):
        return self.__search(item)

    def __str__(self):
        return f'{str(self._data)}'


if __name__ == '__main__':
    a = NamedMapping(**{'e-f': 'ef'})
    assert a.a == 1
    assert a.A == 1
    assert a['a'] == 1
    assert a.b == 'abc'
    assert a['b'] == 'abc'
    assert a.e_f == 'ef'