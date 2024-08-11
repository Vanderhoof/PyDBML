# 1.1.1
- New: SQL and DBML renderers can now be supplied to parser

# 1.1.0

- New: SQL and DBML rendering rewritten tow support external renderers
- New: allow unicode characters in identifiers (DBML v3.3.0)
- New: support for arbitrary table and column properties (#37)

# 1.0.11
- Fix: allow pk in named indexes (thanks @pierresouchay for the contribution)

# 1.0.10
- New: Sticky notes syntax (DBML v3.2.0)
- Fix: Table header color was not rendered in `dbml()` (thanks @tristangrebot for the contribution)
- New: allow array column types (DBML v3.1.0)
- New: allow double quotes in expressions (DBML v3.1.2)
- Fix: recursion in object equality check
- New: don't allow duplicate refs even if they have different inline method (DBML v3.1.6)

# 1.0.9

- Fix: enum collision from different schemas. Thanks @ewdurbin for the contribution

# 1.0.8

- Fix: (#27) allowing comments after Tables, Enums, etc. Thanks @marktaff for reporting

# 1.0.7

- Fix: removing indentation bug

# 1.0.6

- Fix: (#26) bug in note empty line stripping, thanks @Jaschenn for reporting
- New: get_references_for_sql table method

# 1.0.5

- Fix: junction table now has the schema of the first referenced table (as introduced in DBML 2.4.3)
- Fix: typing issue which failed for Python 3.8 and Python 3.9

# 1.0.4

- New: referenced tables in SQL are now defined first in SQL (#23 reported by @minhl)  
- Fix: single quotes were not escaped in column notes (#24 reported by @fivegrant)

# 1.0.3

- Fix: inline many-to-many references were not rendered in sql

# 1.0.2

- New: "backslash newline" is supported in note text (line continuation)
- New: notes have reference to their parent. Note.sql now depends on type of parent (for tables and columns it's COMMENT ON clause)
- New: pydbml no longer splits long notes into multiple lines
- Fix: inline ref schema bug, thanks to @jens-koster
- Fix: (#16) notes were not idempotent, thanks @jens-koster for reporting
- Fix: (#15) note objects were not supported in project definition, thanks @jens-koster for reporting
- Fix: (#20) schema didn't work in table group definition, thanks @mjfii for reporting
- Fix: quotes in note text broke sql and dbml
- New: proper support of composite primary keys without creating an index
- New: support of many-to-many relationships

# 1.0.1

- Fixed setup.py, thanks to @vosskj03.

# 1.0.0

- New project architecture, full support for creating and editing DBML. See details in [Upgrading to PyDBML 1.0.0](docs/upgrading.md)
- New Expression class
- Support DBML 2.4.1 syntax:
    - Multiline comments
    - Multiple schemas

# 0.4.2

- Fix: after editing column name index dbml was not updated.
- Fix: enums with spaces in name were not applied.
- Fix: after editing column name table dict was not updated.
- Fix: after editing enum column type was not updated.
- Removed EnumType class. Only Enum is used now.

# 0.4.1

- Reworked `__repr__` and `__str__` methods on all classes. They are now much simplier and more readable.
- Comments on classes are now rendered as SQL comments in `sql` property (previously notes were rendered as comments on some classes).
- Notes on `Table` and `Column` classes are rendered as SQL comments in `sql` property: `COMMENT ON TABLE "x" is 'y'`.
- New: `dbml` property on most classes and on parsed results which returns the DBML code.
- Fix: sql for Reference and TableReference.

# 0.4.0

- New: Support composite references. **Breaks backward compatibility!** `col1`, `col2` attributes on `Reference` and `col`, `ref_col` attributes on `TableReference` are now lists of `Column` instead of `Column`.
- `TableGroup` now holds references to actual tables.

# 0.3.5

- New: Support references by aliases.
- New: Support indexes with expressions.
- New: You can now compare SQLObjects of same class.
- New: Add check for duplicate references on a table.
- Fix: minor bug fixes.

# 0.3.4

- Notes are now added as comments in SQL for tables, table columns, indeces, enums.

# 0.3.3

- Fix: bug in TableReference
- Fix: if schema had newline or comment at the end, it crashed parser

# 0.3.2

- Fix TableReference sql

# 0.3.1

- Fix: files in **UTF-8 with BOM** encoding couldn't be parsed.

# 0.3

- More tests and more bug fixes.
- Added index columns validation.
- Added table group items validation.
- References now contain link to Table and Column objects instead of just names.
- Indexes now contain link to Column objects instead of just names.

# 0.2

- Better syntax errors.
- sql for each object now contains in `sql` property instead of string rerpresentation. Added proper string representations.
- Added syntax tests.
- Million bugs fixed after testing.

# 0.1.1

- Comments are now parsed too if they are before [b] or on the same line [l] as the entity. Works for: tables[b], columns[lb], references [lb], indexes[lb], enum items [lb], enums [b], project [b] and table group [b]
- All class instances will now have an empty Note in `note` attribute instead of None.
- Add string representation for Note and EnumItem.
- Enum instance now acts like list of EnumItems.
- Add EnumType to use in column.type attribute.
- Column type is now replaced by EnumType instance if enum with such name is defined.
- Remove unnecessary ColumnType class.
- Fix: note definition, project definition, some other definitions

# 0.1

- Initial release
