# Creating DBML schema

You can use PyDBML not only for parsing DBML files, but also for creating schema from scratch in Python.

## Database object

You always start by creating a Database object. It will connect all other entities of the database for us.

```python
>>> from pydbml import Database
>>> db = Database()

```

Now let's create a table and add it to the database.

```python
>>> from pydbml.classes import Table
>>> table1 = Table(name='products')
>>> db.add(table1)

```

To add columns to the table you have to use the `add_column` method of the Table object.

```python
>>> from pydbml.classes import Column
>>> col1 = Column(name='id', type='Integer', pk=True, autoinc=True)
>>> table1.add_column(col1)
>>> col2 = Column(name='product_name', type='Varchar', unique=True)
>>> table1.add_column(col2)
>>> col3 = Column(name='manufacturer_id', type='Integer')
>>> table1.add_column(col3)

```

Index is also a part of a table, so you have to add it similarly, using `add_index` method:

```python
>>> from pydbml.classes import Index
>>> index1 = Index([col2], unique=True)
>>> table1.add_index(index1)

```

The table's third column, `manufacturer_id`. looks like it should be a foreign key. Let's create another table, called `manufacturers`, so that we could create a relation.

```python
>>> table2 = Table(
...     'products',
...     columns=[
...         Column('id', type='Integer', pk=True, autoinc=True),
...         Column('manufacturer_name', type='Varchar'),
...         Column('manufacturer_country', type='Varchar')
...     ]
... )
>>> db.add(table2)
<Table 'public' 'products'>

```

Now to the relation:

```python
from pydbml.classes import Reference
>>> ref = Reference('>', table1['manufacturer_id'], table2['id'])
>>> db.add(ref)

```

You noticed that we are calling the `add` method on the Database after creating each object. While objects can somewhat function without being added to a database, DBML/SQL generation and some other useful methods won't work properly.

Now let's generate DBML code for our schema. This is done by just calling the `dbml` property of the Database object:

```python
>>> print(db.dbml)
>>> #breakpoint()
```
