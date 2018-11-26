
# A class made specifically to find road wins.

class Graph:
    arcs = []

    def __init__( self, grid ):
         self.arcs = self.gridToArcs( grid )

    def gridToArcs( self, grid ):
        size = len(grid)
        col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        rowMaster = ['1', '2', '3', '4', '5', '6', '7', '8']
        row = rowMaster[size-1::-1]
        nodes = {   'left': [],
                    'right':[],
                    'top':[],
                    'bottom':[] }
        for y in range(size):
            for x in range(size):
                if grid[y][x] == 'x':
                    connections = []
                    if x == 0:
                        connections += ['left']
                        nodes['left'] += [col[x]+row[y]]
                    else:
                        if grid[y][x-1] == 'x': connections += [col[x-1]+row[y]]
                    if x == size - 1:
                        connections += ['right']
                        nodes['right'] += [col[x]+row[y]]
                    else:
                        if grid[y][x+1] == 'x': connections += [col[x+1]+row[y]]
                    if y == 0:
                        connections += ['top']
                        nodes['top'] += [col[x]+row[y]]
                    else:
                        if grid[y-1][x] == 'x': connections += [col[x]+row[y-1]]
                    if y == size - 1:
                        connections += ['bottom']
                        nodes['bottom'] += [col[x]+row[y]]
                    else:
                        if grid[y+1][x] == 'x': connections += [col[x]+row[y+1]]
                    nodes[col[x]+row[y]]=connections
        return nodes

    def find_path( self, start, end, exclude = [], path=[] ):
        path = path + [start]
        if start == end:
            return path
        if start not in self.arcs:
            return None
        for node in self.arcs[start]:
            # Exclude added to avoid using the psuedo-nodes created for each side
            if node not in path and node not in exclude:
                newpath = self.find_path( node, end, exclude, path )
                if newpath: return newpath
        return None
