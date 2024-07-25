# Arbitrary Properties

Since 1.1.0 PyDBML supports arbitrary properties in Table and Column definitions. Arbitrary properties is a dictionary of key-value pairs that can be added to any Table or Column manually, or parsed from a DBML file. This may be useful for extending the standard DBML syntax or keeping additional information in the schema.

Arbitrary properties are turned off by default. To enable parsing properties in DBML files, set `allow_properties` argument to `True` in the parser call. To enable rendering properties in the output DBML of an existing database, set `allow_properties` database attribute to `True`.

## Properties in DBML

In a DBML file arbitrary properties are defined like this:

```python
>>> dbml_str = '''
... Table "products" {
...     "id" integer
...     "name" varchar [col_prop: 'some value']
...     table_prop: 'another value'
... }'''

```

In this example we've added a property `col_prop` to the column `name` and a property `table_prop` to the table `products`. Note that property values must me single-quoted strings. Multiline strings (with `'''`) are supported.

Now let's parse this DBML string:

```python
>>> from pydbml import PyDBML
>>> mydb = PyDBML(dbml_str, allow_properties=True)
>>> mydb.tables[0].columns[1].properties
{'col_prop': 'some value'}
>>> mydb.tables[0].properties
{'table_prop': 'another value'}

```

The `allow_properties=True` argument is crucial here. Without it, the parser will raise syntax errors.

## Rendering Properties

To render properties in the output DBML, set `allow_properties` attribute of the Database object to `True`. If you parsed the DBML with `allow_properties=True`, the result database will already have this attribute set to `True`.

We will reuse the `mydb` database from the previous example:

```python
>>> print(mydb.allow_properties)
True

```

Let's set a new property on the table and render the DBML:

```python
>>> mydb.tables[0].properties['new_prop'] = 'Multiline\nproperty\nvalue'
>>> print(mydb.dbml)
Table "products" {
    "id" integer
    "name" varchar [col_prop: 'some value']
<BLANKLINE>
    table_prop: 'another value'
    new_prop: '''
    Multiline
    property
    value'''
}

```

As you see, properties are also rendered in the output DBML correctly. But if `allow_properties` is set to `False`, the properties will be ignored:

```python
>>> mydb.allow_properties = False
>>> print(mydb.dbml)
Table "products" {
    "id" integer
    "name" varchar
}

```
