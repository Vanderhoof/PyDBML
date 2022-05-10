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


class UnknownSchemaError(Exception):
    pass


class DBMLError(Exception):
    pass
