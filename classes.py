class ColumnType:
    def __init__(self, name: str, args: str or None):
        self.name = name
        self.args = args

    def __repr__(self):
        return f'ColumnType({self.name}, {self.args})'

    def __str__(self):
        args = '(' + self.args + ')' if self.args else ''
        return self.name + args


class Reference:
    def __init__(self,
                 type_=str,
                 name=None,
                 table1=None,
                 col1=None,
                 table2=None,
                 col2=None):
        self.type = type_
        self.name = name
        self.table1 = table1
        self.col1 = col1
        self.table2 = table2
        self.col2 = col2

    def __repr__(self):
        components = [f"Reference({self.type}"]
        if self.name:
            components.append(f'name={self.name}')
        if self.table1:
            components.append(f'table1={self.table1}')
        if self.col1:
            components.append(f'col1={self.col1}')
        if self.table2:
            components.append(f'table2={self.table2}')
        if self.col2:
            components.append(f'col2={self.col2}')
