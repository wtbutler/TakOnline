
# A list of game-specific errors

class TakException(Exception):
    pass

class TakInputError(TakException):
    pass

class TakExcecutionError(TakException):
    pass

class TakPlayerError(TakException):
    pass
