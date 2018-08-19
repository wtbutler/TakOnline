import re
import errors
import graph

class Board:
    matchData = ''
    size = 0
    board = 0
    board = []

    def __init__( self, size ):
        self.size = size
        self.board = self.getBoard( size )
        self.matchData = re.compile(r'(?P<prefix>(?P<num_moved>[1-8])|(?P<special_piece>[CcSs]))?(?P<location>(?P<column>[a-h])(?P<row>[1-8]))(?P<movement>(?P<direction>[+-<>])(?P<drops>[1-8]{,8})(?P<wall_smash>\*)?$)?')
        # prefix
        # num_moved
        # special_piece
        # location
        # column
        # row
        # movement
        # direction
        # drops
        # wall_smash

    # Functions needed to get an empty board or to get the right piece count
    def getBoard( self, size ):
        if size < 3 or size > 8:
            raise errors.TakExcecutionError( 'Not a valid board size' )
        tempBoard = [['' for x in range( size )] for y in range( size )]
        return tempBoard

    def getPieces( self ):
        flats = [ 10, 15, 21, 30, 40, 50 ]
        capstones = [ 0, 0, 1, 1, 1, 2 ]
        return flats[ self.size - 3 ], capstones[ self.size - 3 ]

    def isMovable( self, start, modifier, drops, stackRemaining ):
        # Determines via recuesion whether the squares are safe to move into for a certain distance
        new = [ start[0] + modifier[0], start[1] + modifier[1] ]
        if -1 in new or self.size in new: return False
        if self.board[new[1]][new[0]] == '':
            if len( drops ) == 1: return True
            dropped = drops[0]
            return self.isMovable( new, modifier, drops[1:], stackRemaining[dropped:] )
        if self.board[new[1]][new[0]][-1] in self.flat:
            if len( drops ) == 1: return True
            dropped = drops[0]
            return self.isMovable( new, modifier, drops[1:], stackRemaining[dropped:] )
        if self.board[new[1]][new[0]][-1] in self.wall:
            if len( drops ) == 1 and stackRemaining in self.capstone: return True
        return None

    def nameToLocation( self, name ):
        col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        row = ['1', '2', '3', '4', '5', '6', '7', '8']
        nameSplit = list( name )
        return [ col.index( nameSplit[0] ), row.index( nameSplit[1] ) ]

    def locationToName( self, coords ):
        col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        row = ['1', '2', '3', '4', '5', '6', '7', '8']
        return ( col[ coords[0] ] + row[ coords[1] ] )

    def getRegex( self, str ):
        return self.matchData.match( str )

    def getModifier( self, dir ):
        modifiers = {   '<': [-1, 0],
                        '>': [1, 0],
                        '-': [0, -1],
                        '+': [0, 1] }
        return modifiers[ dir ]

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

    # Convert '3a1>12'
    # to
    # [ {action: 'pop', count: 3, x: 0, y:0},
    #   {action: 'push', count: 1, x: 1, y:0},
    #   {action: 'push', count: 2, x: 2, y:0}]
    def ptnToSeq( self, ptnText ):
        regexObj = self.getRegex( ptnText )
        if not( regexObj ):
            raise errors.TakPTNFormatError( 'Invalid PTN string' )
        breakdown = regexObj.groupdict()
        actionList = []
        # Special formatting errors catching and zero value fixing
        if breakdown[ 'num_moved' ] and not( breakdown[ 'movement' ] ):
            raise errors.TakPTNFormatError( 'PTN string has both numeric prefix and no movement substring' )
        if breakdown[ 'special_piece' ] and breakdown[ 'movement' ]:
            raise errors.TakPTNFormatError( 'PTN string has both a special piece prefix and a movement substring' )
        if breakdown[ 'movement' ] and not( breakdown[ 'num_moved' ] ):
            breakdown[ 'num_moved' ] = '1'
        if breakdown[ 'movement' ] and not( breakdown[ 'drops' ] ):
            breakdown[ 'drops' ] = breakdown[ 'num_moved' ]
        if breakdown[ 'movement' ]:
            if int( breakdown[ 'num_moved' ] ) != sum( [ int( i ) for i in breakdown[ 'drops' ] ] ):
                raise errors.TakInputError( 'PTN string has differing totals of pieces to be moved and drops' )
            if int( breakdown[ 'num_moved' ] ) > self.size:
                raise errors.TakInputError( 'PTN string has a larger total of pieces picked up than board length' )

        coords = self.nameToLocation( breakdown[ 'location' ] )
        if breakdown[ 'num_moved' ]:
            actionList += [ {   'action': 'pop',
                                'count': int( breakdown[ 'num_moved' ] ),
                                'x': coords[ 0 ],
                                'y': coords[ 1 ] } ]

        if not( breakdown[ 'movement' ] ):
            if breakdown[ 'special_piece' ]:
                actionList += [ {   'action': 'push',
                                    'count': 1,
                                    'x': coords[ 0 ],
                                    'y': coords[ 1 ],
                                    'special': breakdown[ 'special_piece' ].upper() } ]
            else:
                actionList += [ {   'action': 'push',
                                    'count': 1,
                                    'x': coords[ 0 ],
                                    'y': coords[ 1 ] } ]
        else:
            modifier = self.getModifier( breakdown[ 'direction' ] )
            for submove in range( len( breakdown[ 'drops' ] ) ):
                actionList += [ {   'action': 'push',
                                    'count': int( breakdown[ 'drops' ][ submove ] ),
                                    'x': coords[ 0 ] + modifier[ 0 ] * ( submove + 1 ),
                                    'y': coords[ 1 ] + modifier[ 1 ] * ( submove + 1 ) } ]
        if len( actionList ) == 0:
            raise errors.TakInputError( 'Somehow got through the parser without the parser understanding' )
        return actionList, breakdown, modifier


    # [ {action: 'pop', count: 3, x: 0, y:0},
    #   {action: 'push', count: 1, x: 1, y:0},
    #   {action: 'push', count: 2, x: 2, y:0}]
    # to
    # Convert '3a1>12'
    def seqToPtn( self, seqList ):
        print( 'ptn board' )
        print( self.board )

    def checkOutOfSquares( self ):
        for row in self.board:
            for stack in row:
                if stack == '': return
        self.checkFlatWin()

    def checkRoadWin( self ):
        # Makes separate grids for each player for the possible
        # tiles that player controls that are part of a road
        # i.e. flats and caps but not walls
        roadWhite = False
        roadBlack = False
        whiteGrid = self.getBoard( self.size )
        blackGrid = self.getBoard( self.size )
        for y in range( self.size ):
            for x in range( self.size ):
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
