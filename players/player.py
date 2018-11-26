import copy
import errors
import socket

class Player:
    flatsRemaining = 0
    capstonesRemaining = 0
    playerid = 0
    types = []
    inputMethod = ''
    board = []
    boardSize = 0

    def __init__( self, flats, capstones, channel, playerID, piecesType ):
        self.flatsRemaining = flats
        self.capstonesRemaining = capstones
        self.channel = channel
        self.playerid = playerID
        self.types = piecesType
        self.board = []
        self.boardSize = 0

    def getMove( self ):
        return ''

    def isOutOfPieces( self ):
        if self.flatsRemaining == 0 and self.capstonesRemaining == 0: return True
        return False

    def giveBoard( self, board ):
        self.board = copy.deepcopy( board )
        self.boardSize = len(board)
        self.displayBoard()

    def displayBoard( self ):
        pass

    def useFlat( self ):
        if self.flatsRemaining == 0: raise errors.TakPlayerError( 'Out of flat pieces' )
        self.flatsRemaining -= 1
        return self.types[0]

    def useWall( self ):
        if self.flatsRemaining == 0: raise errors.TakPlayerError( 'Out of flat pieces' )
        self.flatsRemaining -= 1
        return self.types[1]

    def useCapstone( self ):
        if self.capstonesRemaining == 0: raise errors.TakPlayerError( 'Out of capstones' )
        self.capstonesRemaining -= 1
        return self.types[2]
