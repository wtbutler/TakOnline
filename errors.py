
# A list of game-specific errors

class TakException(Exception):
    pass

class TakPTNFormatError(TakException):
    pass

class TakInputError(TakException):
    pass

class TakExcecutionError(TakException):
    pass

class TakPlayerError(TakException):
    pass

class TakBoardError(TakException):
    pass
