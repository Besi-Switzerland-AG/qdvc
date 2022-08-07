===================================
qdvc - Queried Data Version Control
===================================


**Queried Data Version Control** or **QDVC** provides a level of abstraction on `DVC <https://github.com/iterative/dvc>` 
to offer versions control on data that has been queried and how it was queried.

It offers all the benefits of DVC, with:

* storage and versionning of metadata
* versionning of querrying mechanism
* versionning of resulted data from query


Getting Started
===============


+-----------------------+------------------------------------------------------------+
| Task                  | Terminal                                                   |
+-----------------------+------------------------------------------------------------+
| Add data to pool      | | ``$qdvc add images/``                                    |
|                       | | ``$qdvc commit -m 'new images from customer X' -t v2.0`` |
+-----------------------+------------------------------------------------------------+
| Create new Query      | | ``$qdvc create DayTimeData``                             |
|                       | | ``$vim filter.py``                                       |
|                       | | ``$qdvc commit``                                         |
|                       | | ``$qdvc push```                                          |
+-----------------------+------------------------------------------------------------+
| Checkout Queried Data | ``$dqvc checkout DayTimeData v2.0``                        |
+-----------------------+------------------------------------------------------------+
