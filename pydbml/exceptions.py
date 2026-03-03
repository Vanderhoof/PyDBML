class PyDBMLError(Exception):
    """Base class for all PyDBML exceptions."""


class TableNotFoundError(PyDBMLError):
    pass


class ColumnNotFoundError(PyDBMLError):
    pass


class IndexNotFoundError(PyDBMLError):
    pass


class AttributeMissingError(PyDBMLError):
    pass


class DuplicateReferenceError(PyDBMLError):
    pass


class UnknownDatabaseError(PyDBMLError):
    pass


class DBMLError(PyDBMLError):
    pass


class DatabaseValidationError(PyDBMLError):
    pass


class ValidationError(PyDBMLError):
    pass
