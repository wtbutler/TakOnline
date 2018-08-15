class ptnParser:
    board = []

    def __init__( self, board ):
        self.board = board

    # Convert '3a1>12'
    # to
    # [ {action: 'pop', count: 3, x: 0, y:0},
    #   {action: 'push', count: 1, x: 1, y:0},
    #   {action: 'push', count: 2, x: 2, y:0}]
    def ptnToSeq( self, ptnText ):
        pass

    # [ {action: 'pop', count: 3, x: 0, y:0},
    #   {action: 'push', count: 1, x: 1, y:0},
    #   {action: 'push', count: 2, x: 2, y:0}]
    # to
    # Convert '3a1>12'
    def seqToPtn( self, seqList ):
        print( 'ptn board' )
        print( self.board )
