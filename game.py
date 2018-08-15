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
    tileNames = []
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
        self.tileNames = self.getTileList( boardSize )
        if self.board == []: return
        flats, capstones = self.getPieces( boardSize )
        self.white = players.commandLinePlayer.CommandLine( flats, capstones, whiteInput, 0, [ self.flat[0], self.wall[0], self.capstone[0] ] )
        self.black = players.commandLinePlayer.CommandLine( flats, capstones, blackInput, 1, [ self.flat[1], self.wall[1], self.capstone[1] ] )
        self.gameState = gameS.BLACK
        self.parser = ptn.ptnParser( self.board )

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

    def getTileList( self, boardSize ):
        letters = ['1', '2', '3', '4', '5', '6', '7', '8']
        numbers = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        tempTileList = []
        for row in range(boardSize):
            tempRow = []
            for col in range(boardSize):
                tempRow += [numbers[col]+letters[boardSize-1-row]]
            tempTileList += [tempRow]
        return tempTileList

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
        self.parser.seqToPtn( [] )

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
        player.giveBoard( self.board )
        self.checkRoadWin()
        self.checkOutOfPieces()
        self.checkOutOfSquares()

    # Functions for interpreting moves and placing, and moving pieces.
    def moveMaster( self, moveText, player ):
        # moveText sent in a formatted string, but not a list
        if moveText == 'quit':
            self.gameState = gameS.ABORT
            return
        brokenDownText = []
        # REPLACE WITH ACTUAL CONVERSION
        directions = [ '<', '-', '>', '+' ]
        type = ''
        for row in self.tileNames:
            for name in row:
                if name in moveText:
                    offset = moveText.index( name )
                    if offset > 1 or offset < 0: raise error.TakInputError( 'Position value in an incorrect location' )
                    if offset == 1:
                        try:
                            brokenDownText += [ int( moveText[0] ) ]
                        except:
                            brokenDownText += [ moveText[0].upper() ]
                    brokenDownText += [name]
                    if len(moveText) > 2 + offset: type = 'move'
                    else: type = 'place'
                    if type != 'place' and len( moveText ) > 2:
                        if moveText[ 2 + offset ] in directions:
                            brokenDownText += moveText[ 2 + offset ]
                            for i in moveText[ 3 + offset: ]: brokenDownText += [ int( i ) ]
        print( brokenDownText )

        if type == 'move':
            self.moveMove( brokenDownText, player )
            return
        if type == 'place':
            self.movePlace( brokenDownText, player )
            return
        raise errors.TakInputError( 'ERROR: could not decide what kind of move that was' )
        print( 'ERROR: could not decide what kind of move that was' )
        return

    def movePlace( self, moveText, player ):
        # moveText [ <piece type>, location ]
        piece = ''
        moveName = ''
        if len( moveText ) == 1:
            piece = player.types[0]
            moveName += ''
        if len( moveText ) == 2:
            if self.turnCount == 1: raise errors.TakExcecutionError( 'Must play a flat stone on first turn' )
            if moveText[0].lower() == player.types[1].lower():
                piece = player.types[1]
                moveName += 'S'
            if moveText[0].lower() == player.types[2].lower():
                piece = player.types[2]
                moveName += 'C'
        coords = self.nameToLocation( moveText[-1] )
        if self.isEmpty( coords[0], coords[1] ):
            if piece == player.types[2]: player.useCapstone()
            else: player.useFlat()
            self.board[coords[1]][coords[0]] += piece
            moveName += moveText[-1]
            print( moveName )
            self.moveHistory += [ moveName ]
        else:
            raise errors.TakExcecutionError( ' - There is already a piece there.' )
            print( ' - There is already a piece there.' )

    def moveMove( self, moveText, player ):
        # moveText [ <pieces picked up>, location, direction, drop1, drop2, drop3...]
        moveName = ''.join( str(x) for x in moveText )
        print( moveName )
        numMoving = 1
        location = []
        direction = ''
        drops = []
        if type( moveText[0] ) == int: numMoving = moveText.pop(0)
        location = self.nameToLocation( moveText[0] )
        direction = moveText[1]
        drops = moveText[2:]
        if drops == []: drops = [numMoving]
        if self.board[location[1]][location[0]] == '':
            raise errors.TakExcecutionError( 'Trying to move pieces from an empty square' )
            return
        if self.board[location[1]][location[0]][-1] not in player.types:
            raise errors.TakExcecutionError( 'Trying to pick up a piece that is not yours' )
            return
        if len(self.board[location[1]][location[0]]) < numMoving:
            raise errors.TakExcecutionError( 'Trying to pick up more pieces than are in the square' )
            return
        if sum(drops) != numMoving:
            raise errors.TakExcecutionError( 'Trying to drop off a different number of pieces that you picked up' )
            return
        if numMoving > self.boardSize:
            raise errors.TakExcecutionError( 'Trying to pick up more than the carry limit' )
            return
        isCapstone = False
        if self.board[location[1]][location[0]][-1] == player.types[2]:
            path = self.isMovableWithCapstone( location, direction, len(drops), drops[-1] )
            isCapstone = True
            print( 'Capstone path decided' )
        else:
            path = self.isMovable( location, direction, len(drops) )
        if path:
            stack = self.board[location[1]][location[0]]
            tempStack = stack[len(stack)-numMoving:]
            self.board[location[1]][location[0]] = stack[:len(stack)-numMoving]
            print( path )
            for space in path:
                toDrop = drops.pop(0)
                print( tempStack, toDrop )
                if drops == [] and isCapstone:
                    print( 'capstone coming down for final move' )
                    if len( self.board[space[1]][space[0]] ) > 0:
                        print( 'capstone landing on something' )
                        if self.board[space[1]][space[0]][-1] in self.wall:
                            print( 'capstone landing on a wall!' )
                            temp = self.flat[ self.wall.index(self.board[space[1]][space[0]][-1]) ]
                            self.board[space[1]][space[0]] = self.board[space[1]][space[0]][-1][:-1] + temp
                self.board[space[1]][space[0]] += tempStack[:toDrop]
                tempStack = tempStack[toDrop:]
            self.moveHistory += [moveName]
        else:
            raise errors.TakExcecutionError( 'Not possible to move that way' )

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
