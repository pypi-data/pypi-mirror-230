class DQLError(RuntimeError):
    pass


class NotFoundError(Exception):
    pass


class DatasetNotFoundError(NotFoundError):
    pass


class StorageNotFoundError(NotFoundError):
    pass


class PendingIndexingError(Exception):
    """An indexing operation is already in progress."""


class QueryScriptCompileError(Exception):
    pass


class QueryScriptRunError(Exception):
    pass


class QueryScriptDatasetNotFound(Exception):
    pass


class ClientError(RuntimeError):
    def __init__(self, message, error_code=None):
        super().__init__(message)
        # error code from the cloud itself
        self.error_code = error_code


class InconsistentSignalType(Exception):
    pass
