
import players.player

class CommandLine( players.player.Player ):

    def __init__( self, flats, capstones, channel, playerID, piecesType ):
        self.flatsRemaining = flats
        self.capstonesRemaining = capstones
        self.channel = channel
        self.playerid = playerID
        self.types = piecesType
        self.board = []
        self.boardSize = 0

    def getMove( self ):
        # return ['a1']
        return input('What will you do? ')

    def displayBoard( self ):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
        verticalWrapper = [''] + letters[:self.boardSize] + ['']
        print( verticalWrapper )
        for index in range(self.boardSize):
            print( [numbers[self.boardSize-1-index]] + self.board[index] + [numbers[self.boardSize-1-index]] )
        print( verticalWrapper )
        print()
        print( 'Flats remaining: {}, capstones remaining: {}'.format( self.flatsRemaining, self.capstonesRemaining ) )
