[![](https://img.shields.io/pypi/v/pydbml.svg)](https://pypi.org/project/pydbml/)  [![](https://img.shields.io/github/v/tag/Vanderhoof/PyDBML.svg?label=GitHub)](https://github.com/Vanderhoof/PyDBML)

# DBML parser for Python

> The parser is currently on alpha stage. It doesn't have any tests or docstrings yet.

PyDBML is a Python parser for [DBML](https://www.dbml.org) syntax.

## Installation

You can install PyDBML using pip:

```bash
pip install pydbml
```

## Quick start

Import the `PyDBML` class and initialize it with path to DBML-file:

```python
>>> from pydbml import PyDBML
>>> from pathlib import Path
>>> p = PyDBML(Path('schema.dbml'))

```

or with file stream:
```python
>>> with open('schema.dbml') as f:
...     p = PyDBML(f)

```

or with entire source string:
```python
>>> with open('schema.dbml') as f:
...     source = f.read()
>>> p = PyDBML(source)

```

You can access tables inside the `tables` attribute:

```python
>>> for table in p.tables:
...     print(table.name)
...
orders
order_items
products
users
merchants
countries

```

Or just by getting items directly:

```python
>>> p['countries']
Table('countries', [Column('code', 'int', pk=True), Column('name', 'varchar'), Column('continent_name', 'varchar')])
>>> p[1]
Table('order_items', [Column('order_id', 'int'), Column('product_id', 'int'), Column('quantity', 'int', default=1)])

```

Other meaningful attributes are:

* **refs** — list of all references,
* **enums** — list of all enums,
* **table_groups** — list of all table groups,
* **project** — the Project object, if was defined.

Finally, you can get the SQL for your DBML schema by accessing `sql` property:

```python
>>> print(p.sql)  # doctest:+ELLIPSIS
CREATE TYPE "orders_status" AS ENUM (
  'created',
  'running',
  'done',
  'failure',
);
CREATE TYPE "product status" AS ENUM (
  'Out of Stock',
  'In Stock',
);
CREATE TABLE "orders" (
  "id" int PRIMARY KEY AUTOINCREMENT,
  "user_id" int UNIQUE NOT NULL,
  "status" orders_status,
  "created_at" varchar
);
...

```
