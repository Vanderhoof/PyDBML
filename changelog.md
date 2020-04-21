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
