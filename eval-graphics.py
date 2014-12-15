

if __name__ == '__main__' :
    from sys import argv
    from time import sleep
    import COINFLIP
    from graphics import *

    path1 = argv[1]
    path2 = argv[2]

    with open(path1,'r') as f :
        prog1 = COINFLIP.CP_Parser.parse_code(f.read())

    with open(path2,'r') as f :
        prog2 = COINFLIP.CP_Parser.parse_code(f.read())


    x_size,y_size = 40,30
    bots_par_team = int(argv[3])
    smap = [[1 for _ in xrange(x_size)]] + [[1] + [0 for _ in xrange(x_size - 2)] + [1] for _ in xrange(y_size - 2)] + [[1 for _ in xrange(x_size)]]
    smap[-3][-3] = 1
    arena = Arena(smap)

    progs = {'tom' : prog1, 'jerry' : prog2}

    bots = []
    used_pos = {}
    for i in xrange(bots_par_team) :
        for player in progs.keys() :
            pos = None
            while pos == None or pos in used_pos :
                pos = (randint(1,x_size - 2), randint(1,y_size - 2))
            orient = randint(0,3) * 90            
            bots.append( Bot(progs[player],player,position=pos,orientation=orient) )
    
    g = Game(arena,bots)
    
    screen_res = 800,600
    cocos.director.director.init(screen_res[0],screen_res[1])
    scene = GameScreen(g)
    cocos.director.director.run(scene)


