jsonfile
========

version 0.0.9

The ``jsonfile`` Python module can be used to sync a JSON file on a disk with the corresponding Python object instance.

Can be used to autosave JSON compatible Python data.

```python
>>> import jsonfile
>>> dump_kwargs = dict(ensure_ascii=False, indent="\t", sort_keys=True)
>>> a = jsonfile.jsonfile("a.json", autosave=True, dump_kwargs=dump_kwargs)
>>> a.data
Ellipsis
>>> # Ellipsis indicates no data
...
>>> a.data = ["Hello", {"World": "!"}, 1234]
>>> # a.json is now saved
...
>>> del a
>>> # a.json has not been deleted; that would require an explicit a.delete()
...
>>> a
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'a' is not defined
>>> # lets reload the file!
>>>
>>> a = jsonfile.jsonfile("a.json", autosave=True, dump_kwargs=dump_kwargs)
>>> a.data
['Hello', {'World': '!'}, 1234]
>>> a.data.insert(1, "beautiful")
>>> a.data
['Hello', 'beautiful', {'World': '!'}, 1234]
>>> # naturally, also saved
...
>>> a.data = {"Hello":"World!"}
>>> # and saved again...
...
>>> a.delete()
```
