# Upgrading to PyDBML 1.0.0

When I created PyDBML back in April 2020, I just needed a DBML parser, and it was written as a parser. When people started using it, they wanted to also be able to edit DBML schema in Python and create it from scratch. While it worked to some extent, the project architecture was not completely ready for such usage.

In May 2022 I've rewritten PyDBML from scratch and released version 1.0.0. Now you can not only parse DBML files, but also create them in Python and edit parsed schema. Sadly, it made the new version completely incompatible with the old one. This article will help you upgrade to PyDBML 1.0.0 and adapt your code to work with the new version.

## Getting Tables From Parse Results by Name

Previously the parser returned the `PyDBMLParseResults` object, now it returns a `Database` object. While they mostly can be operated similarly, now you can't get a table just by name.

Since v2.4 DBML supports multiple schemas for tables and enums. PyDBML 1.0.0 also supports multiple schemas, but this means that there may be tables with the same name in different schemas. So now you can't get a table from the parse results just by name, you have to specify the schema too:

```python
>>> from pydbml import PyDBML
>>> db = PyDBML.parse_file('test_schema.dbml')
>>> db['orders']
Traceback (most recent call last):
...
KeyError: 'orders'
>>> db['public.orders']
<Table 'public' 'orders'>

```

## New Table Object

Previously the `Table` object had a `refs` attribute which holded a list of `TableReference` objects. `TableReference` represented a table relation and duplicated the `Reference` object of `PyDBMLParseResults` container.

**In 1.0.0 the `TableReference` class is removed, and there's no `Table.refs` attribute.**

Now each relation is represented by a single `Reference` object. You can still access `Table` references by calling the `get_refs` method.

`Table.get_refs` will return a list of References for this table, but only if this table is on the left side of DBML relation.

Here's an example DBML reference definition:

```python
>>> source = '''
... Table posts {
...     id integer [primary key]
...     user_id integer
... }
... 
... Table users {
...     id integer
... }
... 
... Ref name_optional: posts.user_id > users.id
... '''
>>> db = PyDBML(source)

```

Here the many-to-one (`>`) relation is defined with the **posts** table on the left side, so calling `get_refs` on the **posts** table will return you this reference:

```python
>>> db['public.posts'].get_refs()
[<Reference '>', ['user_id'], ['id']>]

```

But calling `get_refs` on the **users** table won't give you the reference, because **users** is on the right side of the relation:

```python
>>> db['public.users'].get_refs()
[]

```

This depends on the side the table was referenced on, not on the type of the reference. So, if we modify the previous example to use one-to-many relation instead of many-to-one:

```python
>>> source = '''
... Table posts {
...     id integer [primary key]
...     user_id integer
... }
... 
... Table users {
...     id integer
... }
... 
... Ref name_optional: users.id < posts.user_id
... '''
>>> db = PyDBML(source)

```

Now the **users** table is on the left, and we can only get the reference from the **users** table:

```python
>>> db['public.users'].get_refs()
[<Reference '<', ['id'], ['user_id']>]
>>> db['public.posts'].get_refs()
[]

```

You can still get all the references for the database by accessing `Database.refs` property:

```python
>>> db.refs
[<Reference '<', ['id'], ['user_id']>]

```

## New Reference Object

Reference now can be explicitly inline. This is defined by the `Reference.inline` attribute. The `inline` attribute only affects how the reference will be rendered in table's SQL or DBML.

Let's define an inline reference.

```python
>>> from pydbml import Database
>>> from pydbml.classes import Table, Column, Reference
>>> db = Database()
>>> table1 = Table('products')
>>> db.add(table1)
< Table
'public' 'products' >
>>> c1 = Column('name', 'varchar2')
>>> table1.add_column(c1)
>>> table2 = Table('names')
>>> db.add(table2)
< Table
'public' 'names' >
>>> c2 = Column('name_val', 'varchar2')
>>> table2.add_column(c2)
>>> ref = Reference('>', c1, c2, inline=True)
>>> db.add(ref)
< Reference
'>', ['name'], ['name_val'] >
>>> print(table1.sql)
CREATE
TABLE
"products"(
    "name"
varchar2,
FOREIGN
KEY("name")
REFERENCES
"names"("name_val")
);

```

If the reference is not inline, it won't appear in the Table SQL definition, otherwise it will be rendered separately as an `ALTER TABLE` clause:

```python
>>> ref.inline = False
>>> print(table1.sql)
CREATE TABLE "products" (
  "name" varchar2
);
>>> print(ref.sql)
ALTER TABLE "products" ADD FOREIGN KEY ("name") REFERENCES "names" ("name_val");

```

## `type_` -> `type`

Previously you would initialize a `Column`, `Index` and `Reference` type with `type_` parameter. Now, this parameter is renamed to simply `type`.

```python
>>> from pydbml.classes import Index, Column
>>> c = Column(name='name', type='varchar')
>>> c
< Column
'name', 'varchar' >
>>> t = Table('names')
>>> t.add_column(c)
>>> i = Index(subjects=[c], type='btree')
>>> t.add_index(i)
>>> i
< Index
'names', ['name'] >
>>> t2 = Table('names_caps', columns=[Column('name_caps', 'varchar')])
>>> ref = Reference(type='-', col1=t['name'], col2=t2['name_caps'])
>>> ref
< Reference
'-', ['name'], ['name_caps'] >

```

## New Expression Class

SQL expressions are allowed in column's `default` value definition and in index's subject definition. Previously, you defined expressions as parenthesized strings: `"(upper(name))"`. Now you have to use the `Expression` class. This will make sure the expression will be rendered properly in SQL and DBML.

```python
>>> from pydbml.classes import Expression
>>> c = Column(
    ...
name = 'upper_name',
...
type = 'varchar',
...
default = Expression('upper(name)')
... )
>>> t = Table('names')
>>> t.add_column(c)
>>> db = Database()
>>> db.add(t)
< Table
'public' 'names' >
>>> print(c.sql)
"upper_name"
varchar
DEFAULT(upper(name))
>>> print(c.dbml)
"upper_name"
varchar[default: `upper(name)`]

```
