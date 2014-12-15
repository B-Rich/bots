

class Arena :
    def __init__(self,arenamap) :
        
        if len(set(map(len,arenamap))) != 1 :
            raise ValueError("Wrong map format")

        self.size = len(arenamap[0]),len(arenamap)
        self.map = {}
        for y in xrange(self.size[1]) :
            for x in xrange(self.size[0]) :
                self.map[(x,y)] = 'FLOOR' if arenamap[y][x] == 0 else 'WALL'
