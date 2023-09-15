import collections.abc
from abc import ABCMeta, abstractmethod


# noinspection PyUnresolvedReferences
class Mapping(collections.abc.Mapping, metaclass=ABCMeta):
    """Default implementation using self._data for storage

    Implement __init__ to populate self._data"""

    @abstractmethod
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f'{str(self._data)}'
