class DatabaseError(Exception):
    pass


class DeleteError(DatabaseError):
    pass


class SaveError(DatabaseError):
    def __init__(self, message: str, column: str = None):
        super().__init__(message)
        self.column = column


class EntityError(DatabaseError):

    def __init__(self, key, message: str = None):
        self._key = key
        super().__init__(message if message else f"Entity error accured: {key}")
