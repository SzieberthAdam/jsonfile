jsonfile
========

version 0.1.1

The ``jsonfile`` Python module can be used to sync a JSON file on a disk with the corresponding Python object instance.

Can be used to autosave JSON compatible Python data.

By default the content of the JSON file is human readable and version control friendly.

**WARNING! This results an extremely slow backend!**

> ### New host with newer version: https://codeberg.org/szieberth-adam/jsonfile
> 
> Archived on GitHub, as I am leaving because of the 2FA enforcement.  -- SzieberthAdam


```python
>>> import jsonfile
>>> a = jsonfile.jsonfile("a.json")
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
>>> a = jsonfile.jsonfile("a.json")
>>> a.data
['Hello', {'World': '!'}, 1234]
>>> a.data.insert(1, "beautiful")
>>> # naturally, also saved
>>> a.data
['Hello', 'beautiful', {'World': '!'}, 1234]
>>> a.data = {"Hello":"World!"}
>>> # and saved again...
>>> a.delete()
>>> # file is deleted but the `a` object still persist
>>> a.save()
>>> # a.json file is recreated;
>>> # note that you can turn on autosaving with `a.autosave=False`
>>> # to avoid excessive disk usage and do explicit saves with this call
>>> o = a.data.copy()
>>> o
{'Hello': 'World!'}
>>> # this is a native Python representation of the internal data;
>>> # changes made on it will not effect the content of the file
>>> o["foo"] = "bar"
>>> o
{'Hello': 'World!', 'foo': 'bar'}
>>> a.data = o
>>> # now however, the file content is updated with it and saved
```
