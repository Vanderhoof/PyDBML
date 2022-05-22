from .base import SQLObject


class Expression(SQLObject):
    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        '''
        >>> print(Expression('sum(amount)'))
        sum(amount)
        '''

        return self.text

    def __repr__(self) -> str:
        '''
        >>> Expression('sum(amount)')
        Expression('sum(amount)')
        '''

        return f'Expression({repr(self.text)})'

    @property
    def sql(self) -> str:
        return f'({self.text})'

    @property
    def dbml(self) -> str:
        return f'`{self.text}`'
