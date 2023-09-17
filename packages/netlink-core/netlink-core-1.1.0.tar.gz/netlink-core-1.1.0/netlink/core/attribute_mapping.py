import collections.abc


def _resolve_iterable(value):
    temp = []
    for i in value:
        if isinstance(i, (str, bytes)):
            temp.append(i)
            continue
        if isinstance(i, collections.abc.Mapping):
            temp.append(AttributeMapping(i))
            continue
        elif isinstance(i, collections.abc.Iterable):
            temp.append(_resolve_iterable(i))
            continue
        temp.append(i)
    return tuple(temp)


class AttributeMapping(collections.abc.Mapping):
    __slots__ = ("_data", '_case_insensitive', '_under')

    def __init__(self, value: collections.abc.Mapping, deep: bool = True, case_sensitive: bool = False, under: bool = True, *args, **kwargs):
        """

        :param value: Mapping
        :param deep: Make contained mappings AttributeMapping
        :param case_sensitive: respect case for items and attributes
        :param under: if true, search for dash (-) if under (_) is not found
        """
        self._data = {k: v for k, v in value.items()}
        self._case_insensitive = not case_sensitive
        self._under = under
        if deep:
            for i in self._data:
                if isinstance(self._data[i], (str, bytes)):
                    continue
                if isinstance(self._data[i], collections.abc.Mapping):
                    self._data[i] = AttributeMapping(self._data[i])
                    continue
                if isinstance(self._data[i], collections.abc.Iterable):
                    self._data[i] = _resolve_iterable(self._data[i])

    def _resolve_deep(self, value):
        if isinstance(value, (str, bytes)):
            return value
        if isinstance(value, collections.abc.Mapping):
            return self.__class__(value, case_sensitive=self._case_sensitive, under=self._under)
        if isinstance(self._data[value], collections.abc.Iterable):
            return tuple([self._resolve_deep(i) for i in value])
        return value

    def __getitem__(self, item):
        if item not in self._data:
            if self._case_insensitive or self._under:
                for i in self._data:
                    if self._case_insensitive:
                        if i.lower() == item.lower():
                            return self._data[i]
                        if self._under and i.lower().replace('-', '_') == item.lower():
                            return self._data[i]
                    elif i.replace('-', '_') == item:
                        return self._data[i]
            raise KeyError(item)
        return self._data[item]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getattr__(self, item):
        if item.startswith('_'):
            return None
        try:
            return self[item]
        except KeyError:
            raise AttributeError(item)

    def __repr__(self):
        return f'{str(self._data)}'
