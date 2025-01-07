
* [Database](#database)
* [Table](#table)
* [Column](#column)
* [Index](#index)
* [Reference](#reference)
* [Enum](#enum)
* [Note](#note)
* [StickyNote](#sticky_note)
* [Expression](#expression)
* [Project](#project)
* [TableGroup](#tablegroup)

# Class Reference

PyDBML classes represent database entities. They live in the `pydbml.classes` package.

```python
>>> from pydbml.classes import Table, Column, Reference

```

The `Database` class represents a PyDBML database. You can import it from the `pydbml` package.

```python
>>> from pydbml import Database

```

## Database

`Database` is the main class, representing a PyDBML database. When PyDBML parses a .dbml file, it returns a `Database` object. This object holds all objects of the database and makes sure they are properly connected. You can access the `Database` object by calling the `database` property of each class (except child classes like `Column` or `Index`).

When you are creating PyDBML schema from scratch, you have to add each created object to the database by calling `Database.add`.

`Database` object may act as a list or a dictionary of tables:

```python
>>> from pydbml import PyDBML
>>> db = PyDBML.parse_file('test_schema.dbml')
>>> table = db.tables[0]
>>> db['public.orders']
<Table 'public' 'orders'>
>>> db[0]
<Table 'public' 'orders'>

```

### Attributes

* **tables** (list of `Table`) — list of all `Table` objects, defined in this database.
* **table_dict** (dict of `Table`) — dictionary holding database `Table` objects. The key is full table name (with schema: `public.mytable`) or a table alias (`myalias`).
* **refs** (list of `Reference`) — list of all `Reference` objects, defined in this database.
* **enums** (list of `Enum`) — list of all `Enum` objects, defined in this database.
* **table_groups** (list of `TableGroup`) — list of all `TableGroup` objects, defined in this database.
* **project** (`Project`) — database `Project`.
* **sql** () — SQL definition for this database.
* **dbml** () — DBML definition for this table.

### Methods

* **add** (PyDBML object) — add a PyDBML object to the database.
* **add_table** (`Table`) — add a `Table` object to the database.
* **add_reference** (`Reference`) — add a `Reference` object to the database.
* **add_enum** (`Enum`) — add a `Enum` object to the database.
* **add_table_group** (`TableGroup`) — add a `TableGroup` object to the database.
* **add_project** (`Project`) — add a `Project` object to the database.
* **delete** (PyDBML object) — delete a PyDBML object from the database.
* **delete_table**  (`Table`) — delete a `Table` object from the database. 
* **delete_reference**  (`Reference`) — delete a `Reference` object from the database. 
* **delete_enum**  (`Enum`) — delete a `Enum` object from the database. 
* **delete_table_group**  (`TableGroup`) — delete a `TableGroup` object from the database. 
* **delete_project**  (`Project`) — delete a `Project` object from the database. 

## Table

`Table` class represents a database table.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> table = parsed.tables[0]
>>> table
<Table 'public' 'orders'>

```

`Table` object may act as a list or a dictionary of columns:

```python
>>> table[0]
<Column 'id', 'int'>
>>> table['status']
<Column 'status', 'orders_status'>

```

### Attributes

* **database** (`Database`) — link to the table's database object, if it was set.
* **name** (str) — table name.
* **schema** (str) — table schema name.
* **full_name** (str) — table name with schema prefix.
* **columns** (list of `Column`) — table columns.
* **indexes** (list of `Index`) — indexes, defined for the table.
* **alias** (str) — table alias, if defined.
* **note** (str) — note for table, if defined.
* **header_color** (str) — the header_color param, if defined.
* **comment** (str) — comment, if it was added just before table definition.
* **sql** (str) — SQL definition for this table.
* **dbml** (str) — DBML definition for this table.

### Methods

* **add_column** (c: `Column`) — add a column to the table,
* **delete_column** (c: `Column` or int) — delete a column from the table by Column object or column index.
* **add_index** (i: `Index`) —  add an index to the table,
* **delete_index** (i: Index or int) — delete an index from the table by Index object or index number.
* **get_refs** — get list of references, defined for this table.
* **get_references_for_sql** — get list of references where this table is on the left side of FOREIGN KEY definition in SQL.

## Column

`Column` class represents a column of a database table.

Table columns are stored in the `columns` attribute of a `Table` object.

### Attributes

* **database** (`Database`) — link to the database object of this column's table, if it was set.
* **name** (str) — column name,
* **table** (`Table`) — link to `Table` object, which holds this column.
* **type** (str or `Enum`) — column type. If type is a enum, this attribute will hold a link to corresponding `Enum` object.
* **unique** (bool) — indicates whether the column is unique.
* **not_null** (bool) — indicates whether the column is not null.
* **pk** (bool) — indicates whether the column is a primary key.
* **autoinc** (bool) — indicates whether this is an autoincrement column.
* **default** (str or bool or int or float or Expression) — column's default value.
* **note** (Note) — column's note if was defined.
* **comment** (str) — comment, if it was added just before column definition or right after it on the same line.
* **sql** (str) — SQL definition for this column.
* **dbml** (str) — DBML definition for this column.

### Methods

* **get_refs** — get list of references, defined for this column.

## Index

`Index` class represents an index of a database table.

Indexes are stored in the `indexes` attribute of a `Table` object.

### Attributes

* **subjects** (list of `Column` or `Expression`) — list subjects which are indexed. Columns are represented by `Column` objects or `Expression` objects.
* **subject_names** (list of str) — list of index subject names.
* **table** (`Table`) — link to table, for which this index is defined.
* **name** (str) — index name, if defined.
* **unique** (bool) — indicates whether the index is unique.
* **type** (str) — index type, if defined. Can be either `hash` or `btree`.
* **pk** (bool) — indicates whether this a primary key index.
* **note** (note) — index note, if defined.
* **comment** (str) — comment, if it was added just before index definition.
* **sql** (str) — SQL definition for this index.
* **dbml** (str) — DBML definition for this index.

## Reference

`Reference` class represents a database relation.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> parsed.refs[0]
<Reference '<', ['id'], ['order_id']>

```

### Attributes

* **database** (`Database`) — link to the reference's database object, if it was set.
* **type** (str) — reference type, in DBML syntax:
  * `<` — one to many;
  * `>` — many to one;
  * `-` — one to one.
* **col1** (list of `Column`) — list of Column objects of the left side of the reference. Changed in **0.4.0**, previously was plain `Column`.
* **table1** (`Table` or `None`) — link to the left `Table` object of the reference or `None` of it was not set.
* **col2** (list of `Column`) — list of Column objects of the right side of the reference. Changed in **0.4.0**, previously was plain `Column`.
* **table2** (`Table` or `None`) — link to the right `Table` object of the reference or `None` of it was not set.
* **name** (str) — reference name, if defined.
* **on_update** (str) — reference's on update setting, if defined.
* **on_delete** (str) — reference's on delete setting, if defined.
* **comment** (str) — comment, if it was added before reference definition.
* **inline** (bool) — indicates whether this reference should be rendered inside SQL or DBML definition of the table.
* **sql** (str) — SQL definition for this reference.
* **dbml** (str) — DBML definition for this reference.

## Enum

`Enum` class represents a enum type in the database.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> enum = parsed.enums[0]
>>> enum
<Enum 'orders_status', ['created', 'running', 'done', 'failure']>

```

Enum objects also act as a list of items:

```python
>>> enum[0]
<EnumItem 'created'>

```

### Attributes

database
name
schema
comment
items

* **database** (`Database`) — link to the enum's database object, if it was set.
* **schema** (str) — enum schema name.
* **name** (str) — enum name,
* **items** (list of `EnumItem`) — list of items.
* **comment** (str) — comment, which was defined before enum definition.
* **sql** (str) — SQL definition for this enum.
* **dbml** (str) — DBML definition for this enum.

### Methods

* **add_item** (item: `EnumItem` or str) — add an item to this enum.

### EnumItem

`EnumItem` class represents an item of a enum type in the database.

Enum items are stored in the `items` property of a `Enum` class.

### Attributes

* **name** (str) — enum item name,
* **note** (`Note`) — enum item note, if was defined.
* **comment** (str) — comment, which was defined before enum item definition or right after it on the same line.
* **sql** (str) — SQL definition for this enum item.
* **dbml** (str) — DBML definition for this enum item.

## Note

Note is a basic class, which may appear in some other classes' `note` attribute. Mainly used for documentation of a DBML database.

### Attributes

**text** (str) — note text.
* **sql** (str) — SQL definition for this note.
* **dbml** (str) — DBML definition for this note.

## Note

**new in PyDBML 1.0.10**

Sticky notes are similar to regular notes, except that they are defined at the root of your DBML file and have a name.

### Attributes

**name** (str) — note name.
**text** (str) — note text.
* **dbml** (str) — DBML definition for this note.

## Expression

**new in PyDBML 1.0.0**

`Expression` class represents an SQL expression. Expressions may appear in `Index` subjects or `Column` default values.

### Attributes

**text** (str) — expression text.
* **sql** (str) — SQL definition for this expression.
* **dbml** (str) — DBML definition for this expression.

## Project

`Project` class holds DBML project metadata. Project is not present in SQL.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> parsed.project
<Project 'test_schema'>

```

### Attributes

* **database** (`Database`) — link to the project's database object, if it was set.
* **name** (str) — project name,
* **items** (str) — dictionary with project metadata,
* **note** (`Note`) — note, if was defined,
* **comment** (str) — comment, if was added before project definition.
* **dbml** (str) — DBML definition for this project.

## TableGroup

`TableGroup` class represents a table group in the DBML database. TableGroups are not present in SQL.

```python
>>> from pydbml import PyDBML
>>> parsed = PyDBML.parse_file('test_schema.dbml')
>>> parsed.table_groups
[<TableGroup 'g1', ['users', 'merchants']>, <TableGroup 'g2', ['countries', 'orders']>]

```

### Attributes

* **database** (`Database`) — link to the tableg group's database object, if it was set.
* **name** (str) — table group name,
* **items** (str) — dictionary with tables in the group,
* **comment** (str) — comment, if was added before table group definition.
* **note** (Note) — table group's note if was defined.
* **dbml** (str) — DBML definition for this table group.
