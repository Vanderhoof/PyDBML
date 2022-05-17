# 1.0.0

- refs don't have tables, only columns
- tables don't have refs
- col1 col2 in ref are as they were in dbml
- Expression class
- add multiline comment

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
