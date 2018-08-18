# Board is a 2d array of fixed size
# Pieces are written left to right in order from bottom up
# Player one is uppercase, player two is lowercase
# Capstone is C/c, Standing stone is S/s, Flat stone is F/f
import enum

import players.player
import players.commandLinePlayer

import graph

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
        self.board = self.getBoard( boardSize )
        if self.board == []: return
        flats, capstones = self.getPieces( boardSize )
        self.white = players.commandLinePlayer.CommandLine( flats, capstones, whiteInput, 0, [ self.flat[0], self.wall[0], self.capstone[0] ] )
        self.black = players.commandLinePlayer.CommandLine( flats, capstones, blackInput, 1, [ self.flat[1], self.wall[1], self.capstone[1] ] )
        self.gameState = gameS.BLACK
        self.parser = ptn.ptnParser( self.boardSize )

        self.firstTurn()
        while self.gameState == gameS.BLACK:
            self.turn()

    # Functions needed to get an empty board or to get the right piece count
    def getBoard( self, boardSize ):
        if boardSize < 3 or boardSize > 8:
            print('Not a legal board size')
            return []
        tempBoard = [['' for x in range( boardSize )] for y in range( boardSize )]
        return tempBoard

    def getPieces( self, boardSize ):
        flats = [ 10, 15, 21, 30, 40, 50 ]
        capstones = [ 0, 0, 1, 1, 1, 2 ]
        return flats[ boardSize - 3 ], capstones[ boardSize - 3 ]

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
        if self.gameState == gameS.BLACK: print('White to move...')

    def isSane( self ):
        for row in self.board:
            for stack in row:
                if len(stack) > 1:
                    for piece in stack[:-1]:
                        if piece == self.wall[0] or piece == self.wall[1]: return False
                        if piece == self.capstone[0] or piece == self.capstone[1]: return False
        return True

    def isEmpty( self, x, y ):
        return self.board[y][x] == ''

    def isMovable( self, start, direction, distance, path = [] ):
        # Determines via recuesion whether the squares are safe to move into for a certain distance
        new = []
        if direction == '<':
            if start[0] == 0: return None
            new = [ start[0] - 1, start[1] ]
        if direction == '>':
            if start[0] == self.boardSize - 1: return None
            new = [ start[0] + 1, start[1] ]
        if direction == '+':
            if start[1] == 0: return None
            new = [ start[0], start[1] - 1 ]
        if direction == '-':
            if start[1] == self.boardSize - 1: return None
            new = [ start[0], start[1] + 1 ]
        if self.board[new[1]][new[0]] == '':
            if distance == 1: return path + [new]
            return self.isMovable( new, direction, distance - 1, path + [new] )
        if self.board[new[1]][new[0]][-1].lower() == self.flat[0].lower():
            if distance == 1: return path + [new]
            return self.isMovable( new, direction, distance - 1, path + [new] )
        return None

    def isMovableWithCapstone( self, start, direction, distance, lastCount, path = [] ):
        # Determines via recuesion whether the squares are safe to move into for a certain distance
        new = []
        if direction == '<':
            if start[0] == 0: return None
            new = [ start[0] - 1, start[1] ]
        if direction == '>':
            if start[0] == self.boardSize - 1: return None
            new = [ start[0] + 1, start[1] ]
        if direction == '+':
            if start[1] == 0: return None
            new = [ start[0], start[1] - 1 ]
        if direction == '-':
            if start[1] == self.boardSize - 1: return None
            new = [ start[0], start[1] + 1 ]
        if self.board[new[1]][new[0]] == '':
            if distance == 1: return path + [new]
            return self.isMovableWithCapstone( new, direction, distance - 1, lastCount, path + [new] )
        if self.board[new[1]][new[0]][-1].lower() == self.flat[0].lower():
            if distance == 1: return path + [new]
            return self.isMovableWithCapstone( new, direction, distance - 1, lastCount, path + [new] )
        if self.board[new[1]][new[0]][-1].lower() == self.wall[0].lower() and lastCount == 1 and distance == 1:
            return path + [new]
        return None

    def boardIsFull( self ):
        for row in self.board:
            for stack in row:
                if stack == '': return
        self.checkFlatWin()

    def nameToLocation( self, name ):
        col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        rowMaster = ['1', '2', '3', '4', '5', '6', '7', '8']
        row = rowMaster[self.boardSize-1::-1]
        nameSplit = list( name )
        coords = [ col.index( nameSplit[0] ), row.index( nameSplit[1] ) ]
        if coords[0] >= self.boardSize: return
        if coords[1] >= self.boardSize: return
        return coords

    def locationToName( self, coords ):
        if coords[0] >= self.boardSize: return
        if coords[1] >= self.boardSize: return
        col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        rowMaster = ['1', '2', '3', '4', '5', '6', '7', '8']
        row = rowMaster[self.boardSize-1::-1]
        return ( col[ coords[0] ] + row[ coords[1] ] )

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
        self.checkRoadWin()
        self.checkOutOfPieces()
        self.checkOutOfSquares()

    # Functions for interpreting moves and placing, and moving pieces.
    def moveMaster( self, moveText, player ):
        if moveText == 'quit':
            self.gameState = gameS.ABORT
            return
        actionList = self.parser.ptnToSeq( moveText )
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
            tempStack = self.popPieces( [ actionList[ 0 ][ 'x' ], actionList[ 0 ][ 'y' ] ], actionList[ 0 ][ 'count' ] )
            print( tempStack )
            for drop in actionList[1:]:
                if drop[ 'action' ] == 'push':
                    self.pushPieces( [ drop[ 'x' ], drop[ 'y' ] ], tempStack[ :drop[ 'count' ] ] )
                    tempStack = tempStack[ drop[ 'count' ]: ]
                else:
                    raise errors.TakExcecutionError( 'You are not able to pick up pieces after your initial submove' )

    def pushPieces( self, coords, piecesToPush ):
        # Returns nothing
        print( coords, piecesToPush )
        if len( self.board[ coords[ 1 ] ][ coords[ 0 ] ] ) > 0:
            if self.board[ coords[ 1 ] ][ coords[ 0 ] ][ -1 ] in self.wall:
                if piecesToPush in self.capstone:
                    temp = self.flat[ self.wall.index( self.board[ coords[ 1 ] ][ coords[ 0 ] ][ -1 ] ) ]
                    self.board[ coords[ 1 ] ][ coords[ 0 ] ] = self.board[ coords[ 1 ] ][ coords[ 0 ] ][ :-1 ] + temp + piecesToPush
                    return
                raise errors.TakExcecutionError( 'Cannot move a piece over a wall' )
            if self.board[ coords[ 1 ] ][ coords[ 0 ] ][ -1 ] in self.capstone:
                raise errors.TakExcecutionError( 'Cannot move a piece over a capstone' )
        print( self.board[ coords[ 1 ] ][ coords[ 0 ] ], piecesToPush )
        self.board[ coords[ 1 ] ][ coords[ 0 ] ] += piecesToPush
        print( self.board[ coords[ 1 ] ][ coords[ 0 ] ] )
        return

    def popPieces( self, coords, numToPop ):
        # Returns string of pieces popped
        tempStack = self.board[ coords[ 1 ] ][ coords[ 0 ] ][ len( self.board[ coords[ 1 ] ][ coords[ 0 ] ] ) - numToPop: ]
        self.board[ coords[ 1 ] ][ coords[ 0 ] ] = self.board[ coords[ 1 ] ][ coords[ 0 ] ][ :len( self.board[ coords[ 1 ] ][ coords[ 0 ] ] ) - numToPop ]
        return tempStack


    # Functions for determining if a winner exists
    def checkOutOfPieces( self ):
        # Pretty self explanatory
        if self.white.isOutOfPieces() or self.black.isOutOfPieces():
            self.checkFlatWin()

    def checkOutOfSquares( self ):
        for row in self.board:
            for stack in row:
                if stack == '': return
        self.checkFlatWin()

    def checkFlatWin( self ):
        # Totals up flat pieces on top of stacks and gives
        # the win to the person with the most
        count1 = 0
        count2 = 0
        for row in self.board:
            for stack in row:
                if len(stack) > 0:
                    if stack[-1] == self.flat[0]: count1 += 1
                    if stack[-1] == self.flat[1]: count2 += 1
        if count1 > count2: self.gameState = gameS.WHITE_TILE
        if count2 > count1: self.gameState = gameS.BLACK_TILE
        if count1 == count2: self.gameState = gameS.DRAW
        return

    def checkRoadWin( self ):
        # Makes separate grids for each player for the possible
        # tiles that player controls that are part of a road
        # i.e. flats and caps but not walls
        roadWhite = False
        roadBlack = False
        whiteGrid = self.getBoard( self.boardSize )
        blackGrid = self.getBoard( self.boardSize )
        for y in range( self.boardSize ):
            for x in range( self.boardSize ):
                if self.board[y][x] != '':
                    if self.board[y][x][-1] == self.flat[0] or self.board[y][x][-1] == self.capstone[0]: whiteGrid[y][x] = 'x'
                    if self.board[y][x][-1] == self.flat[1] or self.board[y][x][-1] == self.capstone[1]: blackGrid[y][x] = 'x'
        # Creates a graph object out of these grids so a pact can be found
        whiteGraph = graph.Graph( whiteGrid )
        blackGraph = graph.Graph( blackGrid )
        # Looks for a path from each side to each opposite side,
        # excluding the pseudo-nodes of the sides themselves
        if whiteGraph.find_path('left', 'right', [ 'top', 'bottom' ] ) != None: roadWhite = True
        if whiteGraph.find_path('top', 'bottom', [ 'left', 'right' ] ) != None: roadWhite = True
        if blackGraph.find_path('left', 'right', [ 'top', 'bottom' ] ) != None: roadBlack = True
        if blackGraph.find_path('top', 'bottom', [ 'left', 'right' ] ) != None: roadBlack = True
        print( whiteGraph.find_path('left', 'right', [ 'top', 'bottom' ] ) )
        print( whiteGraph.find_path('top', 'bottom', [ 'left', 'right' ] ) )
        print( blackGraph.find_path('left', 'right', [ 'top', 'bottom' ] ) )
        print( blackGraph.find_path('top', 'bottom', [ 'left', 'right' ] ) )
        # Gives the road to the player who won, or the active player in the case
        # of a double road.
        if roadWhite and not roadBlack:
            self.gameState = gameS.WHITE_ROAD
        if roadBlack and not roadWhite:
            self.gameState = gameS.BLACK_ROAD
        if roadWhite and roadBlack:
            if self.gameState == gameS.WHITE: self.gameState = gameS.WHITE_ROAD
            if self.gameState == gameS.BLACK: self.gameState = gameS.BLACK_ROAD
