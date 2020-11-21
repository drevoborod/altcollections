class TupleDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        if type(item) in (int, slice):
            return tuple(self.values())[item]
        else:
            return dict.__getitem__(self, item)

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]
        else:
            return dict.__getattribute__(self, item)

    def __setattr__(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        if isinstance(key, int):
            raise TypeError(f'Integers cannot be added as '
                            f'{self.__class__.__name__} keys')
        else:
            dict.__setitem__(self, key, value)

    def crop(self, key):
        """Deletes provided key from the dictionary and returns dictionary."""
        del self[key]
        return self

    def crop_astuple(self, key):
        """Deletes provided key from the dictionary and
        returns tuple of values."""
        del self[key]
        return self[:]
