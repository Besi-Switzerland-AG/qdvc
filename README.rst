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
