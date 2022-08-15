===================================
qdvc - Queried Data Version Control
===================================


**Queried Data Version Control** or **QDVC** provides a level of abstraction on `DVC <https://github.com/iterative/dvc>` 
to offer versions control on data that has been queried and how it was queried.

It offers all the benefits of DVC, with:
* versionning of querrying mechanism
* versionning of data filtered from query


Getting Started
===============


+-----------------------+------------------------------------------------------------+
| Task                  | Terminal                                                   |
+-----------------------+------------------------------------------------------------+
| Add data to pool      | | ``$qdvc add images/``                                    |
|                       | | ``$git commit -m 'new images from customer X' -t v2.0``  |
+-----------------------+------------------------------------------------------------+
| Create new Query      | | ``$qdvc query DayTimeData``                              |
|                       | | ``$vim filter.py``                                       |
|                       | | ``$qdvc commit``                                         |
+-----------------------+------------------------------------------------------------+
| Checkout Queried Data | ``$qdvc checkout DayTimeData v2.0``                        |
+-----------------------+------------------------------------------------------------+


The Querying Mechanism
======================

Queries can be based on the filename or n any metadata. For example, you can `add` a TinyDB json file with some metadata for each file.

The file `filter.py` is used to filter files. It looks like:
```python
from tinydb import TinyDB, Query

class Query:
    def __init__(self):
        self.db = TinyDB("metadata.json")
        pass

    def filter(self, filepath: str) -> bool:
        """
        Determines if the file filepath should be kept in the filtered data.
        Looking in the database if the data associated to the file was not collected during the night.
        """
        file = Query()
        return not self.db.search(file.path == filepath).IsNight
```

For reproducibility, do not use any data that is not checked out in DVC.