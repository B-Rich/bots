from random import randint

class Arena :
    def __init__(self,arenamap) :
        
        if len(set(map(len,arenamap))) != 1 :
            raise ValueError("Wrong map format")

        self.size = len(arenamap[0]),len(arenamap)
        self.map = {}
        for y in xrange(self.size[1]) :
            for x in xrange(self.size[0]) :
                self.map[(x,y)] = 'FLOOR' if arenamap[y][x] == 0 else 'WALL'
    
if __name__ == '__main__' :
    from sys import argv
    import COINFLIP

    path1 = argv[1]
    path2 = argv[2]

    with open(path1,'r') as f :
        prog1 = COINFLIP.CP_Parser.parse_code(f.read())

    with open(path2,'r') as f :
        prog2 = COINFLIP.CP_Parser.parse_code(f.read())

    x_size,y_size = 20,20
    bots_par_team = int(argv[3])
    smap = [[1]*x_size] + [[1] + [0]*(x_size - 2) + [1]]*(y_size - 2) + [[1]*x_size]
    arena = Arena(smap)

    progs = {'tom' : prog1, 'jerry' : prog2}

    bots = []
    used_pos = {}

    # TEST THE SPECIAL CRASH CONDITION
    go_on = COINFLIP.CP_Parser.parse_code("DEFAULT MOVE FORWARD;")
    bot1 = Bot(go_on,'tom',position=(3,3),orientation=0)
    bot2 = Bot(go_on,'jerry',position=(4,3),orientation=180)
    bot3 = Bot(go_on,'jerry',position=(3,4),orientation=270)
    bots = [bot1,bot2,bot3]
    
    '''
    for i in xrange(bots_par_team) :
        for player in progs.keys() :
            pos = None
            while pos == None or pos in used_pos :
                pos = (randint(1,x_size - 2), randint(1,y_size - 2))
            orient = randint(0,3) * 90
            bots.append( Bot(progs[player],player,position=pos,orientation=orient) )
    '''
    g = Game(arena,bots)

    from os import system
    from time import sleep
    system('clear')
    print g.prettyPrint()

    while not g.gameOver() :

#        sleep(0.5)
        raw_input()
        g.turn()
        system('clear')
        print g.prettyPrint()

    print "\n{} WON THE MATCH!".format(g.bots[0].player)





