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

class Game :

    def __init__(self,arena,clear_arena=True) :
        self.arena = arena
        self.clear_arena = clear_arena

    def prettyPrint(self) :
        out = []
        
        for y in xrange(self.arena.size[1]) :
            out.append([])
            for x in xrange(self.arena.size[0]) :
                if self.arena.map[(x,y)] == 'WALL' :
                    out[-1].append('#')
                else :
                    out[-1].append(' ')

        for b in self.bots :
            if b.status == 'OPERATIVE' :
                if b.orientation == 0 :
                    c = '>'
                elif b.orientation == 90 :
                    c = '^'
                elif b.orientation == 180 :
                    c = '<'
                elif b.orientation == 270 :
                    c = 'V'
                else :
                    raise ValueError("Orientation not in [0,90,180,270]")
            else :
                c = '*'
            out[b.position[1]][b.position[0]] = c
        
        s_out = []
        for r in out :
            s_out.append( ''.join(r))

        for b in self.bots :
            s_out.append('BOT - pos: {},{} - ort: {} - sts: {} - act: {} - plr: {}'.format(str(b.position[0]),str(b.position[1]),str(b.orientation),b.status,b.action,b.player))
        return '\n'.join(s_out) + '\n'
        

    def play(self) :
        while not self.gameOver() :
            self.turn()

    def turn(self) :
        self.executePrograms()
        self.evaluateActions()
        if self.clear_arena :
            self.clearUnoperativeBots()

    def gameOver(self) :
        return len(set([bot.player for bot in self.bots if bot.status == 'OPERATIVE'])) <= 1

    def clearUnoperativeBots(self) :
        self.bots = [b for b in self.bots if b.status == 'OPERATIVE']

    def executePrograms(self) :
        for bot in self.bots :
            if bot.status == 'OPERATIVE' :
                bot.execute()

    def evaluateActions(self) :
        '''
        Evaluates the actions in the current turn. Actions are concurrent, and the evaluation order is the following:
        - move
        - shoot
        - turn
        - wait

        '''

        # evaluates MOVE actions
        destinations = {}
        moving_bots = [bot for bot in self.bots if bot.action.startswith('MOVE')]
        # destination of not moving bots is their actual position
        for bot in [b for b in self.bots if not b.action.startswith('MOVE')] :
            destinations[bot.position] = [bot]


#        print "destinations before move: "+str(destinations.keys())
        for bot in moving_bots :

            if bot.action.endswith('FORWARD') :
                moving_dir = bot.orientation
            elif bot.action.endswith('BACKWARD') :
                moving_dir = (bot.orientation + 180) % 360
            elif bot.action.endswith('LEFT') :
                moving_dir = (bot.orientation + 90) % 360
            elif bot.action.endswith('RIGHT') :
                moving_dir = (bot.orientation - 90) % 360
            else :
                raise ValueError("MOVE ??")

            if moving_dir == 0 :
                step = (1,0)
            elif moving_dir == 90 :
                step = (0,-1)
            elif moving_dir == 180 :
                step = (-1,0)
            elif moving_dir == 270 :
                step = (0,1)
            else :
                raise ValueError("Orientation ??")

            next_pos = (bot.position[0] + step[0],bot.position[1] + step[1])
                
            if next_pos in destinations :
                destinations[next_pos].append(bot)
            else :
                destinations[next_pos] = [bot]
        
        # computes the crashes happening :
        # when at least 2 bots collide
        # when the destination is outside the map or is a wall

#        print "destinations before crashes: "+str(destinations.keys())

        crashes = []
        for d in destinations :
            if len(destinations[d]) > 1 : # two or more bot crash on the same destination
                crashes.append(d)
            elif self.arena.map[d] == 'WALL' :
                crashes.append(d)
            elif d[0] < 0 or d[1] < 0 or d[0] >= self.arena.size[0] or d[1] >= self.arena.size[1] : # one or more bots are moving outside the map
                crashes.append(d)

        for crash in crashes :
            for bot in destinations[crash] :
                bot.status = 'CRASHED'
                
#        print "destinations before shooting: "+str(destinations.keys())
        # evaluates the SHOOT actions
        shooting_bots = [bot for bot in self.bots if bot.action == 'SHOOT' and bot.status == 'OPERATIVE']
        for bot in shooting_bots :

            if bot.orientation == 0 :
                step = (1,0)
            elif bot.orientation == 90 :
                step = (0,-1)
            elif bot.orientation == 180 :
                step = (-1,0)
            elif bot.orientation == 270 :
                step = (0,1)
            else :
                raise ValueError("Orientation not in [0,90,180,270]")
            
            target = bot.position
            for i in xrange(bot.fire_range) :
                target = (target[0] + step[0],target[1] + step[1])
                if self.arena.map[target] == 'WALL' :
                    break
                elif target in destinations and len(destinations[target]) == 1 : # if there's only one coming, shoots it, otherwise they'll crash before
                    destinations[target][0].status = 'HIT'
                    break


        # evaluates the TURN actions
        turning_bots = [bot for bot in self.bots if bot.action.startswith('TURN') and bot.status == 'OPERATIVE']
        for bot in turning_bots :
            if bot.action.endswith('LEFT') :
                bot.orientation = (bot.orientation + 90) % 360
            elif bot.action.endswith('RIGHT') :
                bot.orientation = (bot.orientation - 90) % 360
            else :
                raise ValueError("Direction to turn not in [LEFT,RIGHT]")

#        print "destinations after turn: "+str(destinations.keys())
        for d in destinations :
            for bot in destinations[d] :
                if bot.status == 'OPERATIVE' :
                    bot.position = d
    
class Bot :
    def __init__(self,program,player,game,position=None,orientation=None,FOV=2,fire_range=4) :
        self.program = program
        self.player = player
        self.game = game
        self.position = position
        self.orientation = orientation
        self.FOV = FOV
        self.fire_range = fire_range
        self.status = 'OPERATIVE'
        self.action = 'WAIT'

        self.coinflip = None
        self.dice = None

    def sensor(self,x,y) :
        if x > self.FOV or y > self.FOV :
            raise BotException("out of FOV")
        
        
        if self.orientation == 0 :
            bias = x,-y
        elif self.orientation == 90 :
            bias = -y,-x
        elif self.orientation == 180 :
            bias = -x,y
        elif self.orientation == 270 :
            bias = y,x

        abs_pos = (self.position[0] + bias[0],self.position[1] + bias[1])
        if abs_pos[0] < 0 or abs_pos[1] < 0 or abs_pos[0] >= self.game.arena.size[0] or abs_pos[1] >= self.game.arena.size[1] :
            return 'WALL'
        if self.game.arena.map[abs_pos] != 'WALL' :
            retStr = 'FLOOR'
            for bot in self.game.bots :
                if bot.position == abs_pos :
                    retStr += ' BOT'
                    if bot.player != self.player :
                        retStr += ' ENEMY'
                    else :
                        retStr += ' FRIEND'
            return retStr
        return self.game.arena.map[abs_pos]
        
        
    def execute(self) :
        self.coinflip = (randint(0,1) == 0)
        self.dice = randint(1,6)
        try :
            for condition,action in self.program :
                if eval(condition) :
                    exec(action)
                    return
            self.action = 'WAIT'
        except BotException :
            self.status = 'SYS FAULT'

class BotException (Exception) :
    def __init__(self,msg) :
        self.msg = msg
    def __str__(self) :
        return repr(self.msg)

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
    bots_par_team = 5
    smap = [[1]*x_size] + [[1] + [0]*(x_size - 2) + [1]]*(y_size - 2) + [[1]*x_size]
    arena = Arena(smap)

    progs = {'tom' : prog1, 'jerry' : prog2}

    g = Game(arena,clear_arena=True)

    g.bots = []
    used_pos = {}
    for i in xrange(bots_par_team) :
        for player in progs.keys() :
            pos = None
            while pos == None or pos in used_pos :
                pos = (randint(1,x_size - 2), randint(1,y_size - 2))
            orient = randint(0,3) * 90
            g.bots.append( Bot(progs[player],player,g,position=pos,orientation=orient) )
    
    from os import system
    from time import sleep
    system('clear')
    print g.prettyPrint()

    while not g.gameOver() :

        sleep(0.5)
#        raw_input()
        g.turn()
        system('clear')
        print g.prettyPrint()

    print "\n{} WON THE MATCH!".format(g.bots[0].player)
