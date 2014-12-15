

    
if __name__ == '__main__' :
    from sys import argv
    from random import randint
    from os import system
    from time import sleep
    import COINFLIP,arena,bot,game

    path1 = argv[1]
    path2 = argv[2]

    with open(path1,'r') as f :
        prog1 = COINFLIP.CP_Parser.parse_code(f.read())

    with open(path2,'r') as f :
        prog2 = COINFLIP.CP_Parser.parse_code(f.read())

    x_size,y_size = 20,20
    bots_par_team = int(argv[3])
    smap = [[1]*x_size] + [[1] + [0]*(x_size - 2) + [1]]*(y_size - 2) + [[1]*x_size]
    arena = arena.Arena(smap)

    progs = {'tom' : prog1, 'jerry' : prog2}

    bots = []
    used_pos = {}    

    for i in xrange(bots_par_team) :
        for player in progs.keys() :
            pos = None
            while pos == None or pos in used_pos :
                pos = (randint(1,x_size - 2), randint(1,y_size - 2))
            orient = randint(0,3) * 90
            bots.append( bot.EvalBot(progs[player],player,position=pos,orientation=orient) )

    g = game.EvalGame(arena,bots)

    system('clear')
    print g.prettyPrint()

    while not g.gameOver() :

        sleep(0.5)
        g.turn()
        system('clear')
        print g.prettyPrint()

    print "\n{} WON THE MATCH!".format(g.bots[0].player)





