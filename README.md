[![](https://img.shields.io/pypi/v/pydbml.svg)](https://pypi.org/project/pydbml/) [![](https://img.shields.io/pypi/dm/pydbml.svg)](https://pypi.org/project/pydbml/)  [![](https://img.shields.io/github/v/tag/Vanderhoof/PyDBML.svg?label=GitHub)](https://github.com/Vanderhoof/PyDBML)

# DBML parser for Python

*Compliant with DBML **v2.3.0** syntax*

PyDBML is a Python parser for [DBML](https://www.dbml.org) syntax.

## Installation

You can install PyDBML using pip:

```bash
pip3 install pydbml
```

## Quick start

Import the `PyDBML` class and initialize it with path to DBML-file:

```python
>>> from pydbml import PyDBML
>>> from pathlib import Path
>>> parsed = PyDBML(Path('test_schema.dbml'))

```

or with file stream:
```python
>>> with open('test_schema.dbml') as f:
...     parsed = PyDBML(f)

```

or with entire source string:
```python
>>> with open('test_schema.dbml') as f:
...     source = f.read()
>>> parsed = PyDBML(source)

```

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

Or just by getting items by index or table name:

```python
>>> parsed['countries']
<Table 'countries'>
>>> parsed[1]
<Table 'order_items'>

```

Other meaningful attributes are:

* **refs** — list of all references,
* **enums** — list of all enums,
* **table_groups** — list of all table groups,
* **project** — the Project object, if was defined.

You can get the SQL for your DBML schema by accessing `sql` property:

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
  "status" orders_status,
  "created_at" varchar
);
...

```

Finally, you can generate the DBML source from your schema with updated values from the classes (added in **0.4.1**):

```python
>>> parsed.project.items['author'] = 'John Doe'
>>> print(parsed.dbml)  # doctest:+ELLIPSIS
Project test_schema {
    author: 'John Doe'
    Note {
        'This schema is used for PyDBML doctest'
    }
}
<BLANKLINE>
Table "orders" {
    "id" int [pk, increment]
    "user_id" int [unique, not null]
    "status" orders_status
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

# Docs

## Table class

After running parser all tables from the schema are stored in `tables` attribute of the `PyDBMLParseResults` object.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> table = parsed.tables[0]
>>> table
<Table 'orders'>

```

Important attributes of the `Table` object are:

* **name** (str) — table name,
* **refs** (list of `TableReference`) — all foreign keys, defined for the table,
* **columns** (list of `Column`) — table columns,
* **indexes** (list of `Index`) — indexes, defined for the table.
* **alias** (str) — table alias, if defined.
* **note** (str) — note for table, if defined.
* **header_color** (str) — the header_color param, if defined.
* **comment** (str) — comment, if it was added just before table definition.

`Table` object may act as a list or a dictionary of columns:

```python
>>> table[0]
<Column 'id', 'int'>
>>> table['status']
<Column 'status', 'orders_status'>

```

## Column class

Table columns are stored in the `columns` attribute of a `Table` object.

Important attributes of the `Column` object are:

* **name** (str) — column name,
* **table** (Table)— link to `Table` object, which holds this column.
* **type** (str or `Enum`) — column type. If type is a enum, defined in the same schema, this attribute will hold a link to corresponding `Enum` object.
* **unique** (bool) — is column unique.
* **not_null** (bool) — is column not null.
* **pk** (bool) — is column a primary key.
* **autoinc** (bool) — is an autoincrement column.
* **default** (str or int or float) — column's default value.
* **note** (Note) — column's note if was defined.
* **comment** (str) — comment, if it was added just before column definition or right after it on the same line.

## Index class

Indexes are stored in the `indexes` attribute of a `Table` object.

Important attributes of the `Index` object are:

* **subjects** (list of `Column` or `str`) — list subjects which are indexed. Columns are represented by `Column` objects, expressions (`getdate()`) are stored as strings `(getdate())`. Expressions are supported since **0.3.5**.
* **table** (`Table`) — table, for which this index is defined.
* **name** (str) — index name, if defined.
* **unique** (bool) — is index unique.
* **type** (str) — index type, if defined. Can be either `hash` or `btree`.
* **pk** (bool) — is this a primary key index.
* **note** (note) — index note, if defined.
* **comment** (str) — comment, if it was added just before index definition.

## Reference class

After running parser all references from the schema are stored in `refs` attribute of the `PyDBMLParseResults` object.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> parsed.refs[0]
<Reference '<', 'orders'.['id'], 'order_items'.['order_id']>

```

Important attributes of the `Reference` object are:

* **type** (str) — reference type, in DBML syntax:
  * `<` — one to many;
  * `>` — many to one;
  * `-` — one to one.
* **table1** (`Table`) — link to the first table of the reference.
* **col1** (list os `Column`) — list of Column objects of the first table of the reference. Changed in **0.4.0**, previously was plain `Column`.
* **table2** (`Table`) — link to the second table of the reference.
* **col2** (list of `Column`) — list of Column objects of the second table of the reference. Changed in **0.4.0**, previously was plain `Column`.
* **name** (str) — reference name, if defined.
* **on_update** (str) — reference's on update setting, if defined.
* **on_delete** (str) — reference's on delete setting, if defined.
* **comment** (str) — comment, if it was added before reference definition.

## TableReference class

Apart from `Reference` objects, parser also creates `TableReference` objects, which are stored in each table, where the foreign key should be defined. These objects don't have types. List of references is stored in `refs` attribute of a Table object:

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> order_items_refs = parsed.tables[1].refs
>>> order_items_refs[0]
<TableReference ['order_id'], 'orders'.['id']>

```

Important attributes of the `TableReference` object are:

* **col** (list[`Column`]) — list of Column objects, which are referenced in this table. Changed in **0.4.0**, previously was plain `Column`.
* **ref_table** (`Table`) — link to the second table of the reference.
* **ref_col** (list[`Column`]) — list of Column objects, which are referenced by this table. Changed in **0.4.0**, previously was plain `Column`.
* **name** (str) — reference name, if defined.
* **on_update** (str) — reference's on update setting, if defined.
* **on_delete** (str) — reference's on delete setting, if defined.

## Enum class

After running parser all enums from the schema are stored in `enums` attribute of the `PyDBMLParseResults` object.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> enum = parsed.enums[0]
>>> enum
<Enum 'orders_status', ['created', 'running', 'done', 'failure']>

```

`Enum` object contains three attributes:

* **name** (str) — enum name,
* **items** (list of `EnumItem`) — list of items.
* **comment** (str) — comment, which was defined before enum definition.

Enum objects also act as a list of items:

```python
>>> enum[0]
<EnumItem 'created'>

```

### EnumItem class

Enum items are stored in the `items` property of a `Enum` class.

`EnumItem` object contains following attributes:

* **name** (str) — enum item name,
* **note** (`Note`) — enum item note, if was defined.
* **comment** (str) — comment, which was defined before enum item definition or right after it on the same line.

## Note class

Note is a basic class, which may appear in some other classes' `note` attribute. It has just one meaningful attribute:

**text** (str) — note text.

## Project class

After running parser the project info is stored in the `project` attribute of the `PyDBMLParseResults` object.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> parsed.project
<Project 'test_schema'>

```

Attributes of the `Project` object:

* **name** (str) — project name,
* **items** (str) — dictionary with project items,
* **note** (`Note`) — note, if was defined,
* **comment** (str) — comment, if was added before project definition.

## TableGroup class

After running parser the project info is stored in the `project` attribute of the `PyDBMLParseResults` object.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> parsed.table_groups
[<TableGroup 'g1', ['users', 'merchants']>, <TableGroup 'g2', ['countries', 'orders']>]

```

Attributes of the `TableGroup` object:

* **name** (str) — table group name,
* **items** (str) — dictionary with tables in the group,
* **comment** (str) — comment, if was added before table group definition.

> TableGroup `items` parameter initially holds just the names of the tables, but after parsing the whole document, `PyDBMLParseResults` class replaces them with references to actual tables.
