from deepdiff import DeepDiff

from altcollections import ExtendedDict, TupleDict


class DictDiff(DeepDiff):
    """Allows to compare two instances of custom dictionaries and basic dict"""
    def __init__(self, *args, **kwargs):
        if 'ignore_type_in_groups' not in kwargs:
            kwargs['ignore_type_in_groups'] = [
                (dict, ExtendedDict), (dict, TupleDict), (ExtendedDict, TupleDict)]
        super().__init__(*args, **kwargs)
