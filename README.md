[![](https://img.shields.io/pypi/v/pydbml.svg)](https://pypi.org/project/pydbml/) [![](https://img.shields.io/pypi/dm/pydbml.svg)](https://pypi.org/project/pydbml/)  [![](https://img.shields.io/github/v/tag/Vanderhoof/PyDBML.svg?label=GitHub)](https://github.com/Vanderhoof/PyDBML) ![](coverage.svg)

# DBML parser for Python

*Compliant with DBML **v2.5.3** syntax*

PyDBML is a Python parser and builder for [DBML](https://www.dbml.org) syntax. 

> The project was rewritten in May 2022, the new version 1.0.0 is not compatible with versions 0.x.x. See details in [Upgrading to PyDBML 1.0.0](docs/upgrading.md).

**Docs:**

* [Class Reference](docs/classes.md)
* [Creating DBML schema](docs/creating_schema.md)
* [Upgrading to PyDBML 1.0.0](docs/upgrading.md)

> PyDBML requires Python v3.8 or higher

## Installation

You can install PyDBML using pip:

```bash
pip3 install pydbml
```

## Quick start

To parse a DBML file, import the `PyDBML` class and initialize it with Path object

```python
>>> from pydbml import PyDBML
>>> from pathlib import Path
>>> parsed = PyDBML(Path('test_schema.dbml'))

```

or with file stream

```python
>>> with open('test_schema.dbml') as f:
...     parsed = PyDBML(f)

```

or with entire source string

```python
>>> with open('test_schema.dbml') as f:
...     source = f.read()
>>> parsed = PyDBML(source)
>>> parsed
<Database>

```

The parser returns a Database object that is a container for the parsed DBML entities.

You can access tables inside the `tables` attribute:

```python
>>> for table in parsed.tables:
...     print(table.name)
...
orders
order_items
products
users
merchants
countries

```

Or just by getting items by index or full table name:

```python
>>> parsed[1]
<Table 'public' 'order_items'>
>>> parsed['public.countries']
<Table 'public' 'countries'>

```

Other attributes are:

* **refs** — list of all references,
* **enums** — list of all enums,
* **table_groups** — list of all table groups,
* **project** — the Project object, if was defined.

Generate SQL for your DBML Database by accessing the `sql` property:

```python
>>> print(parsed.sql)  # doctest:+ELLIPSIS
CREATE TYPE "orders_status" AS ENUM (
  'created',
  'running',
  'done',
  'failure',
);
<BLANKLINE>
CREATE TYPE "product status" AS ENUM (
  'Out of Stock',
  'In Stock',
);
<BLANKLINE>
CREATE TABLE "orders" (
  "id" int PRIMARY KEY AUTOINCREMENT,
  "user_id" int UNIQUE NOT NULL,
  "status" "orders_status",
  "created_at" varchar
);
...

```

Generate DBML for your Database by accessing the `dbml` property:

```python
>>> parsed.project.items['author'] = 'John Doe'
>>> print(parsed.dbml)  # doctest:+ELLIPSIS
Project "test_schema" {
    author: 'John Doe'
    Note {
        'This schema is used for PyDBML doctest'
    }
}
<BLANKLINE>
Enum "orders_status" {
    "created"
    "running"
    "done"
    "failure"
}
<BLANKLINE>
Enum "product status" {
    "Out of Stock"
    "In Stock"
}
<BLANKLINE>
Table "orders" {
    "id" int [pk, increment]
    "user_id" int [unique, not null]
    "status" "orders_status"
    "created_at" varchar
}
<BLANKLINE>
Table "order_items" {
    "order_id" int
    "product_id" int
    "quantity" int [default: 1]
}
...

```
