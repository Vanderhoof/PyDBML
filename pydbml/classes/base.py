from typing import Any
from typing import Tuple

from pydbml.exceptions import AttributeMissingError


class SQLObject:
    '''
    Base class for all SQL objects.
    '''
    required_attributes: Tuple[str, ...] = ()

    def check_attributes_for_sql(self):
        '''
        Check if all attributes, required for rendering SQL are set in the
        instance. If some attribute is missing, raise AttributeMissingError
        '''
        for attr in self.required_attributes:
            if getattr(self, attr) is None:
                raise AttributeMissingError(
                    f'Cannot render SQL. Missing required attribute "{attr}".'
                )

    def __setattr__(self, name: str, value: Any):
        """
        Required for type testing with MyPy.
        """
        super().__setattr__(name, value)

    def __eq__(self, other: object) -> bool:
        """
        Two instances of the same SQLObject subclass are equal if all their
        attributes are equal.
        """

        if not isinstance(other, self.__class__):
            return False
        # not comparing those because they are circular references
        not_compared_fields = ('parent', 'table', 'database')

        self_dict = dict(self.__dict__)
        other_dict = dict(other.__dict__)

        for field in not_compared_fields:
            self_dict.pop(field, None)
            other_dict.pop(field, None)

        return self_dict == other_dict
        return False
