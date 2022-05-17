class TableNotFoundError(Exception):
    pass


class ColumnNotFoundError(Exception):
    pass


class IndexNotFoundError(Exception):
    pass


class AttributeMissingError(Exception):
    pass


class DuplicateReferenceError(Exception):
    pass


class UnknownDatabaseError(Exception):
    pass


class DBMLError(Exception):
    pass


class DatabaseValidationError(Exception):
    pass
