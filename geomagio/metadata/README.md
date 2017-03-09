# Metadata


## Structure

Each `type` of metadata uses a separate folder,
with one file per `object` being described.

```
geomagio/metadata/TYPE/OBJECT.py
```

Each file defines a `METADATA` variable,
which consists of a list of dictionary objects
that define different versions of metadata associated with an `OBJECT`.


```
"""OBJECT metadata file"""

METADATA = [
    {VERSION2}
    {VERSION1}
]
```


### Epochs (Versions)

Each version represents the metadata for a given time interval.
*Versions must appear in descending order (newest versions first).*


The time interval is represented using the reserved properties
`starttime` and `endtime`, which define the time interval that this version of
metadata are valid.

The interval can be represented using set notation as:
    `[starttime, endtime)`

- `starttime` - ISO8601 formatted string, or `None`

    The time when this version of the metadata is first considered valid.

    When this value is `None`,
    it implies the metadata is valid for all times before `endtime`.

- `endtime` - ISO8601 formatted string, or `None`

    The time when this version of the metadata is no longer valid.

    When this value is `None`,
    it implies the metadata is valid for all times after `starttime`.

#### Examples

This example shows two versions of metadata:
one for all times before `2016-01-01T00:00:00Z`
    (some_value = 1),
and one for all times after and including `2016-01-01T00:00:00Z`
    (some_value = 2).

```python
METADATA = [
    {
        'starttime': '2016-01-01T00:00:00Z',
        'endtime': None

        # other properties
        'some_value': 2
    },
    {
        'starttime': None
        'endtime': '2016-01-01T00:00:00Z'

        # other properties
        'some_value': 1
    }
]
```
