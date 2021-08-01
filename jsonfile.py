"""
The ``jsonfile`` Python module can be used to sync a JSON file on a disk with the
corresponding Python object instance.

Can be used to autosave JSON compatible Python data.

By default the content of the JSON file is human readable and version control
friendly.
"""

__version__ = "0.1.1"



import collections.abc
import copy
import json
import pathlib
import tempfile



class JSONFileBase:

    @property
    def jsonfile(self):
        return self._jsonfile

    @staticmethod
    def _inputvalue(value):
        if isinstance(value, (collections.abc.Mapping, JSONFileObject)):
            return {str(k): JSONFileBase._inputvalue(v) for k, v in value.items()}  # ensure string keys
        elif isinstance(value, str):
            return value
        elif isinstance(value, (collections.abc.Sequence, JSONFileArray)):
            return [JSONFileBase._inputvalue(v) for v in value]
        else:
            return value

    def _outputvalue(self, data):
        if isinstance(data, str):  # string is a special sequence
            return data
        elif isinstance(data, collections.abc.Mapping):
            return JSONFileObject(self._jsonfile, data)
        elif isinstance(data, collections.abc.Sequence):
            return JSONFileArray(self._jsonfile, data)
        else:
            return data



class JSONFileRoot(JSONFileBase):

    # As the main purpose of this module to provide a human readable and version control friendly dynamic data
    # storage, I decided to diverge a little from the default JSON dump parameters.
    default_dump_kwargs = {
        "skipkeys": False,
        "ensure_ascii": False,  # +human readable (UTF)
        "check_circular": True,
        "allow_nan": True,
        "cls": None,
        "indent": "\t",  # +human readable
        "separators": None,
        "default": None,
        "sort_keys": True,  # +version control friendliness
    }

    default_load_kwargs = {
        "cls": None,
        "object_hook": None,
        "parse_float": None,
        "parse_int": None,
        "parse_constant": None,
        "object_pairs_hook": None,
    }

    def __init__(self, path, *, data=..., autosave=True, dump_kwargs=None, load_kwargs=None):
        self._jsonfile = self
        self._data = data
        self.autosave = autosave
        self.dump_kwargs = self.default_dump_kwargs if dump_kwargs is None else dump_kwargs
        self.load_kwargs = self.default_load_kwargs if load_kwargs is None else load_kwargs
        self.path = path
        if data is ...:
            if self.path.is_file():
                self.load()
        else:
            if autosave:
                self.save()

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.path}')"

    def __str__(self):
        return self.__repr__()

    def copy(self, path, *, autosave=..., dump_kwargs=..., load_kwargs=...):
        path = pathlib.Path(path)
        assert path != self.path
        autosave = autosave if autosave is not ... else self.autosave
        dump_kwargs = dump_kwargs if dump_kwargs is not ... else self.dump_kwargs
        load_kwargs = load_kwargs if load_kwargs is not ... else self.load_kwargs
        return JSONFileRoot(
            path,
            data=self._data,
            autosave=autosave,
            dump_kwargs=dump_kwargs,
            load_kwargs=load_kwargs,
        )

    @property
    def data(self):
        return self._outputvalue(self._data)
    @data.setter
    def data(self, value):
        self._data = self._inputvalue(value)
        if self.autosave:
            self.save()

    def delete(self):
        self.path.unlink()

    def load(self):
        p = self.path
        path_exists = p.is_file()
        path_is_not_empty = bool(p.stat().st_size)
        if path_exists and path_is_not_empty:
            with p.open(encoding="utf8") as f:
                self._data = json.load(f, **self.load_kwargs)
        else:
            self._data = ...

    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, value):
        self._path = pathlib.Path(value) # ensure Path instance

    def save(self, *, ensure_parents=True):
        p = self.path
        s = json.dumps(self._data, **self.dump_kwargs)
        if ensure_parents:  # ensure parent directories
            p.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=p.parent, delete=False, encoding="utf8") as tf:
            tf.write(s)
            tp = p.parent / tf.name
        tp.replace(p)



class JSONFileContainer(JSONFileBase):

    _methods_which_cause_change = ()

    def __init__(self, jsonfile, data):
        self._jsonfile = jsonfile
        self._data = data

    def __contains__(self, key):
        return self._data.__contains__(key)

    def __delitem__(self, key):
        self._data.__delitem__(key)
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def __dir__(self):
        return sorted(self._data.__dir__() + ["jsonfile"])

    @property
    def __doc__(self):
        return self._data.__doc__

    def __eq__(self, other):
        return self._data.__eq__(other if not hasattr(other, "_data") else other._data)

    def __getattr__(self, name):
        return getattr(self._data, name)

    def __getitem__(self, key):
        data = self._data[key]
        return self._outputvalue(data)

    def __len__(self):
        return self._data.__len__()

    def __ne__(self, other):
        return self._data.__ne__(other if not hasattr(other, "_data") else other._data)

    def __repr__(self):
        return self._data.__repr__()

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def __sizeof__(self):
        # TODO(adam): not sure about this
        return object.__sizeof__(self) + self._data.__sizeof__()

    def clear(self):
        self._data.clear()
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def copy(self):
        """a deep copy of the internal data"""
        return copy.deepcopy(self._data)



class JSONFileArray(JSONFileContainer, list):

    def __add__(self, value):
        raise AttributeError(
            f"type object {self.__class__.__name__!r} has no attribute '__add__'"
            f"\n{self.__class__.__name__!r} instances are not meant to be created directly"
            "\nHint: you can add in place with the `+=` operator"
            " or you can manipulate the copy of the internal data"
        )

    def __dir__(self):
        names = set(super().__dir__())
        names.remove("__add__")  # JSONFileObject instances are not meant to be created directly
        names.remove("__mul__")  # same reason
        names.remove("__rmul__")  # same reason
        return sorted(names)

    def __ge__(self, other):
        return self._data.__ge__(other if not hasattr(other, "_data") else other._data)

    def __gt__(self, other):
        return self._data.__gt__(other if not hasattr(other, "_data") else other._data)

    def __iadd__(self, other):
        self._data += self._inputvalue(other)
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def __imul__(self, other):
        self._data *= self._inputvalue(other)
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def __iter__(self):
        return JSONFileArray_iterator(self)

    def __le__(self, other):
        return self._data.__le__(other if not hasattr(other, "_data") else other._data)

    def __lt__(self, other):
        return self._data.__lt__(other if not hasattr(other, "_data") else other._data)

    def __mul__(self, value):
        raise AttributeError(
            f"type object {self.__class__.__name__!r} has no attribute '__mul__'"
            f"\n{self.__class__.__name__!r} instances are not meant to be created directly"
            "\nHint: you can multiply in place with the `*=` operator"
            " or you can manipulate the copy of the internal data"
        )

    def __reversed__(self):
        return JSONFileArray_reverseiterator(self)

    def __rmul__(self, value):
        raise AttributeError(
            f"type object {self.__class__.__name__!r} has no attribute '__rmul__'"
            f"\n{self.__class__.__name__!r} instances are not meant to be created directly"
            "\nHint: you can multiply in place with the `*=` operator"
            " or you can manipulate the copy of the internal data"
        )

    def append(self, item):
        self._data.append(self._inputvalue(item))
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def count(self, value):
        return self._data.count(value)

    def extend(self, iterable):
        self._data.extend(self._inputvalue(x) for x in iterable)
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def index(self, value, start=0, stop=9223372036854775807):
        return self._data.index(value, start, stop)

    def insert(self, i, elem):
        self._data.insert(i, self._inputvalue(elem))
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def pop(self, index=-1):
        returnobj = self._data.pop(index)
        if self._jsonfile.autosave:
            self._jsonfile.save()
        return returnobj

    def remove(self, value):
        self._data.remove(value)
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def reverse(self):
        self._data.reverse()
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def sort(self):
        self._data.sort()
        if self._jsonfile.autosave:
            self._jsonfile.save()



class JSONFileArray_iterator():

    def __init__(self, obj):
        self._obj = obj
        self._i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == len(self._obj):
            raise StopIteration
        returnobj = self._obj[self._i]
        self._i += 1
        return returnobj



class JSONFileArray_reverseiterator():

    def __init__(self, obj):
        self._obj = obj
        self._i = -1

    def __iter__(self):
        return self

    def __next__(self):
        if len(self._obj) < -self._i:
            raise StopIteration
        returnobj = self._obj[self._i]
        self._i -= 1
        return returnobj



class JSONFileObject(JSONFileContainer, dict):

    def __dir__(self):
        names = set(super().__dir__())
        names.remove("fromkeys")  # JSONFileObject instances are not meant to be created directly
        return sorted(names)

    def __iter__(self):
        # no need of custom iterator as dict.__iter__ only return the keys
        return self._data.__iter__()

    def __reversed__(self):
        # no need of custom iterator as dict.__reversed__ only return the keys
        return self._data.__reversed__()

    def __setitem__(self, key, value):
        key = str(key)  # ensure that JSON object keys are strings
        return super().__setitem__(key, self._inputvalue(value))

    @classmethod
    def fromkeys(cls, iterable, value=None):
        raise AttributeError(
            f"type object {cls.__name__!r} has no attribute 'fromkeys'"
            f"\n{cls.__name__!r} instances are not meant to be created directly"
        )

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def items(self):
        for k in self:
            yield k, self[k]

    def keys(self):
        return self._data.keys()

    def pop(self, key, default):
        returnobj = self._data.pop(key, default)
        if self._jsonfile.autosave:
            self._jsonfile.save()
        return returnobj

    def popitem(self):
        returnobj = self._data.popitem()
        if self._jsonfile.autosave:
            self._jsonfile.save()
        return returnobj

    def setdefault(self, key, default):
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return self[key]

    def update(self, *args, **kwargs):
        _args = [self._inputvalue(x) for x in args]
        _kwargs = {k: self._inputvalue(v) for k, v in kwargs.items()}
        self._data.update(*_args, **_kwargs)
        if self._jsonfile.autosave:
            self._jsonfile.save()

    def values(self):
        for key in self:
            yield self[key]



jsonfile = JSONFileRoot
