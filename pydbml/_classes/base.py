from typing import Tuple

from pydbml.exceptions import AttributeMissingError


class SQLObject:
    '''
    Base class for all SQL objects.
    '''
    required_attributes: Tuple[str, ...] = ()
    _eq_skip_fields: Tuple[str, ...] = ()

    def check_attributes_for_sql(self) -> None:
        '''
        Check if all attributes, required for rendering SQL are set in the
        instance. If some attribute is missing, raise AttributeMissingError
        '''
        for attr in self.required_attributes:
            if getattr(self, attr) is None:
                raise AttributeMissingError(
                    f'Cannot render SQL. Missing required attribute "{attr}".'
                )
    @property
    def sql(self) -> str:
        if hasattr(self, 'database') and self.database is not None:
            renderer = self.database.sql_renderer
        else:
            from pydbml.renderer.sql.default import DefaultSQLRenderer
            renderer = DefaultSQLRenderer

        return renderer.render(self)

    def __eq__(self, other: object) -> bool:
        """
        Two instances of the same SQLObject subclass are equal if all their
        attributes are equal.
        """

        if not isinstance(other, self.__class__):
            return False

        self_dict = dict(self.__dict__)
        other_dict = dict(other.__dict__)

        for field in self._eq_skip_fields:
            self_dict.pop(field, None)
            other_dict.pop(field, None)

        return self_dict == other_dict


class DBMLObject:
    '''Base class for all DBML objects.'''
    @property
    def dbml(self) -> str:
        if hasattr(self, 'database') and self.database is not None:
            renderer = self.database.dbml_renderer
        else:
            from pydbml.renderer.dbml.default import DefaultDBMLRenderer
            renderer = DefaultDBMLRenderer

        return renderer.render(self)
