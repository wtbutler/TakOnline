# Board is a 2d array of fixed size
# Pieces are written left to right in order from bottom up
# Player one is uppercase, player two is lowercase
# Capstone is C/c, Standing stone is S/s, Flat stone is F/f
import enum

import players.player
import players.commandLinePlayer

import board

import errors

import ptn

gameS = enum.Enum( 'gameS', 'WHITE_ROAD BLACK_ROAD WHITE_TILE BLACK_TILE DRAW WHITE BLACK ABORT NONE')

class Game:
    boardSize = 0
    board = []
    turnCount = 0
    moveHistory = []
    white = 0
    black = 0
    flat = ['F', 'f']
    wall = ['S', 's']
    capstone = ['C', 'c']
    parser = 0
    gameState = gameS.NONE

    def __init__( self, boardSize, whiteInput, blackInput ):
        self.boardSize = boardSize
        self.board = board.Board( self.boardSize )
        flats, capstones = self.board.getPieces()
        self.white = players.commandLinePlayer.CommandLine( flats, capstones, whiteInput, 0, [ self.flat[0], self.wall[0], self.capstone[0] ] )
        self.black = players.commandLinePlayer.CommandLine( flats, capstones, blackInput, 1, [ self.flat[1], self.wall[1], self.capstone[1] ] )
        self.gameState = gameS.BLACK

        self.firstTurn()
        while self.gameState == gameS.BLACK:
            self.turn()

    # Helper functions that check various states
    def updateState( self ):
        if self.gameState == gameS.WHITE_ROAD: print('White wins by road')
        if self.gameState == gameS.WHITE_TILE: print('White wins by flat count')
        if self.gameState == gameS.BLACK_ROAD: print('Black wins by road')
        if self.gameState == gameS.BLACK_TILE: print('Black wins by flat count')
        if self.gameState == gameS.DRAW: print('It\'s a tie!')
        if self.gameState == gameS.ABORT: print('ERROR: ABORT')
        if self.gameState == gameS.NONE: print('ERROR: NONE')
        if self.gameState == gameS.WHITE: print('Black to move...')
        if self.gameState == gameS.BLACK: print('White to move...')board.

    # Main functions of the game, allow changes to be made.
    def firstTurn( self ):
        self.turnCount += 1
        self.gameState = gameS.WHITE
        self.ply( self.black )
        self.updateState()

        if self.gameState != gameS.WHITE: return

        self.gameState = gameS.BLACK
        self.ply( self.white )
        self.updateState()

    def turn( self ):
        self.turnCount += 1
        self.gameState = gameS.WHITE
        self.ply( self.white )
        self.updateState()

        if self.gameState != gameS.WHITE: return

        self.gameState = gameS.BLACK
        self.ply( self.black )
        self.updateState()

    def ply( self, player ):
        moved = False
        player.giveBoard( self.board )
        while not( moved ):
            try:
                move = player.getMove()
                self.moveMaster( move, player )
                moved = True
            except errors.TakException as e:
                print( e )
        # player.giveBoard( self.board )
        self.board.checkRoadWin()
        self.board.checkOutOfPieces()
        self.board.checkOutOfSquares()

    # Functions for interpreting moves and placing, and moving pieces.
    def moveMaster( self, moveText, player ):
        if moveText == 'quit':
            self.gameState = gameS.ABORT
            return
        if moveText[0] == 't':
            self.tellInactivePlayer( player, moveText[1:] )
            return
        actionList, breakdown, modifier = self.parser.ptnToSeq( moveText )
        for action in actionList: print( action )
        # Handles placement
        if len( actionList ) == 1:
            if self.board[ actionList[ 0 ][ 'y' ] ][ actionList[ 0 ][ 'x' ] ]:
                raise errors.TakExcecutionError( 'You must place a new piece in an empty square!' )
            if not( 'special' in actionList[0].keys() ):
                player.useFlat()
                self.pushPieces( [ actionList[ 0 ][ 'x' ], actionList[ 0 ][ 'y' ] ], player.types[ 0 ] )
                return
            if actionList[ 0 ][ 'special' ] == self.capstone[ 0 ]:
                player.useCapstone()
                self.pushPieces( [ actionList[ 0 ][ 'x' ], actionList[ 0 ][ 'y' ] ], player.types[ 2 ] )
                return
            if actionList[ 0 ][ 'special' ] == self.wall[ 0 ]:
                player.useFlat()
                self.pushPieces( [ actionList[ 0 ][ 'x' ], actionList[ 0 ][ 'y' ] ], player.types[ 1 ] )
                return
        else:
            if len( self.board[ actionList[ 0 ][ 'y' ] ][ actionList[ 0 ][ 'x' ] ] ) < actionList[0][ 'count' ]:
                raise errors.TakExcecutionError( 'You cannot pick up more pieces than are in a space' )
            if not ( self.board[ actionList[ 0 ][ 'y' ] ][ actionList[ 0 ][ 'x' ] ][ -1 ] in player.types ):
                raise errors.TakExcecutionError( 'You can only move stacks that you control' )
            tempStack = self.board[ actionList[ 0 ] ][ actionList[ 0 ][ 'y' ] ][ len( self.board[ coords[ 1 ] ][ coords[ 0 ] ] ) - numToPop: ]
            self.isMovable( [ actionList[ 0 ][ 'x' ], actionList[ 0 ][ 'y' ] ], modifier, breakdown['drops'], tempStack )
            tempStack = self.popPieces( [ actionList[ 0 ][ 'x' ], actionList[ 0 ][ 'y' ] ], actionList[ 0 ][ 'count' ] )
            print( tempStack )
            for drop in actionList[1:]:
                if drop[ 'action' ] == 'push':
                    self.pushPieces( [ drop[ 'x' ], drop[ 'y' ] ], tempStack[ :drop[ 'count' ] ] )
                    tempStack = tempStack[ drop[ 'count' ]: ]
                else:
                    raise errors.TakExcecutionError( 'You are not able to pick up pieces after your initial submove' )
