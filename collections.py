class ExtendedDict(dict):
    """
    Расширение базового словаря. Новые возможности:
    - возможность доступа и добавления ключей через точечную нотацию.
        То есть можно добавить как ключ (d['key'] = 1), а можно - как атрибут:
        d.key1 = 2. Доступ после этого будет возможен как через ключ,
        так и через атрибут: d['key'] или d.key. Для тех, кому надоело писать
        скобочки и кавычки. При этом выгодное отличие от данных в виде объектов -
        сохранение плюшек словаря: методы keys и items, итератор, update и т.д.
    - поддержка операции умножения. При этом возвращается новый экземпляр
        ExtendedDict, у которого все значения умножены на предоставленное число.
        Удобно, когда нужно увеличить все значения в словаре на что-то одно.
        Прочие арифметические операции пока не поддерживаются за ненадобностью,
        но, может будет добавлено в будущем.
    - новый метод crop: возвращает НОВЫЙ экземпляр ExtendedDict,
        из которого выкинут соответствующий ключ.
        Нужно для однострочников. Метод оригинального словаря pop меняет
        исходный словарь, поэтому требуется создавать экземпляр словаря,
        потом делать в нём pop отдельной строкой, а потом уже использовать
        получившийся результат. А в ExtendedDict можно сделать так:
        `return cls.date_time(**ExtendedDict(locals()).crop('cls')`
        Здесь мы из словаря locals выкидываем ключ 'cls' и сразу же
        к получившемуся результату применяем date_time(). Это удобно,
        потому что не нужно заводить отдельную переменную вроде
        "params = locals()" - у нас автоматически создаётся копия,
        из которой при применении метода crop опять же возвращается копия.
        В случае с pop нам бы вернулось значение удаляемого ключа, что далеко
        не всегда нужно.
    - новый метод add: расширение метода update, которое позволит не изменять
        исходный словарь, а возвращать новый экземпляр с изменениями.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # All inner dictionaries will be recursively converted to ExtendedDict.
        for key, value in self.items():
            self[key] = value

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]
        else:
            return dict.__getattribute__(self, item)

    def __setattr__(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, DictConverter.convert(value, self.__class__))

    def __mul__(self, other):
        """
        Returns new instance of ExtendedDict instantiated from 'self' where all
        values of root keys are multiplied on value of 'other' (not recursive).
        """
        new = self.__class__(self)
        for key, value in new.items():
            try:
                new[key] = value * other
            except TypeError:
                raise TypeError(f"can't multiply value of key '{key}' "
                                f"by non-int of type '{type(other).__name__}'")
        return new

    def crop(self, *keys):
        """Deletes provided keys from the dictionary and returns new ExtendedDict."""
        new = self.__class__(self)
        for key in keys:
            new.pop(key, None)
        return new

    def add(self, __m=None, /, **kwargs):
        """Adds provided dictionary to current and returns new copy of ExtendedDict."""
        new = self.__class__(self)
        new.update(__m, **kwargs)
        return new

    def replace(self, key, value):
        """Return new copy of ExtendedDict and replace provided key in it."""
        new = self.__class__(self)
        new[key] = value
        return new

    def update(self, __m=None, /, **kwargs) -> None:
        if __m:
            dict.update(self, DictConverter.convert(__m, self.__class__),
                        **DictConverter.convert(kwargs, self.__class__))
        else:
            dict.update(self, **DictConverter.convert(kwargs, self.__class__))

    def copy(self):
        return self.__class__(dict.copy(self))


class TupleDict(ExtendedDict):
    """
    - добавлена возможность доступа по срезу и индексу непосредственно к значениям
        (их порядок сохраняется), то есть:
            d['key'] = 1
            d['key1'] = 2
        d[0] вернёт 1, который мы выше добавили
        d[:] вернёт кортеж (1, 2).
        У этого есть побочный эффект:
        невозможно обратиться к ключам, имеющим тип int, поскольку такие обращения
        автоматически считаются обращением по индексу. Но кто в реальной жизни
        использует словари с int в качестве ключей? Встречается редко.
        И, если встретится, всегда можно использовать обычный словарь :)
    - новый метод crop_astuple: возвращает кортеж из значений словаря,
        из которого убрано значение, соответствующее ключу словаря, переданному методу.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        if type(item) in (int, slice):
            return tuple(self.values())[item]
        else:
            return dict.__getitem__(self, item)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            raise TypeError(f'Integers cannot be added as '
                            f'{self.__class__.__name__} keys')
        else:
            self.__class__.__bases__[0].__setitem__(self, key, value)

    def crop_astuple(self, *keys):
        """Deletes provided keys from the dictionary and
        returns tuple of values of new TupleDict."""
        new = self.__class__(self)
        for key in keys:
            new.pop(key, None)
        return new[:]


class DictConverter:
    """"""

    dest_class = ExtendedDict

    @classmethod
    def convert(cls, source, dest_class):
        cls.dest_class = dest_class
        return cls._check_type(source)

    @classmethod
    def _check_type(cls, value):
        if hasattr(value, 'keys'):
            return cls._convert_dict(value)
        elif isinstance(value, (list, tuple, set)):
            return cls._convert_array(value)
        return value

    @classmethod
    def _convert_dict(cls, dictionary):
        result = cls.dest_class(dictionary)
        for key, value in result.items():
            result[key] = cls._check_type(value)
        return result

    @classmethod
    def _convert_array(cls, array):
        t = type(array)
        return t([cls._check_type(item) for item in array])
