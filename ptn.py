import re
import errors

class ptnParser:
    matchData = ''
    boardSize = 0

    def __init__( self, boardSize ):
        self.boardSize = boardSize
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
            if int( breakdown[ 'num_moved' ] ) > self.boardSize:
                raise errors.TakInputError( 'PTN string has a larger total of pieces picked up than board length' )
        coords = self.nameToLocation( breakdown[ 'location' ] )
        if breakdown[ 'num_moved' ]:
            actionList += [ {   'action': 'pop',
                                'count': int( breakdown[ 'num_moved' ] ),
                                'x': coords[ 0 ],
                                'y': coords[ 1 ] } ]
        if breakdown[ 'special_piece' ]:
            actionList += [ {   'action': 'push',
                                'count': 1,
                                'x': coords[ 0 ],
                                'y': coords[ 1 ],
                                'special': breakdown[ 'special_piece' ].upper() } ]

        if not( breakdown[ 'movement' ] ):
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

        return actionList


    # [ {action: 'pop', count: 3, x: 0, y:0},
    #   {action: 'push', count: 1, x: 1, y:0},
    #   {action: 'push', count: 2, x: 2, y:0}]
    # to
    # Convert '3a1>12'
    def seqToPtn( self, seqList ):
        print( 'ptn board' )
        print( self.board )
