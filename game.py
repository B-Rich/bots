
class Game :

    def __init__(self,arena,bots) :
        self.arena = arena
        self.bots = bots
        self.players = list(set([b.player for b in self.bots]))

        for bot in self.bots :
            bot.game = self

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
        
        # mirrors the y axis
        out.reverse()
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

    def gameOver(self) :
        return len(set([bot.player for bot in self.bots if bot.status == 'OPERATIVE'])) <= 1

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

        # bots to evaluate are those that start the turn as operative
        bots_to_eval = [b for b in self.bots if b.status == 'OPERATIVE']


        # evaluates MOVE actions
        destinations = {}
        moving_bots = [bot for bot in bots_to_eval if bot.action.startswith('MOVE')]
        # destination of not moving bots is their actual position
        for bot in [b for b in bots_to_eval if not b.action.startswith('MOVE')] :
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
                step = (0,1)
            elif moving_dir == 180 :
                step = (-1,0)
            elif moving_dir == 270 :
                step = (0,-1)
            else :
                raise ValueError("Orientation ??")

            next_pos = (bot.position[0] + step[0],bot.position[1] + step[1])

            # manages the case * (see below)
            for other_bot in moving_bots :
                # if bot1 destination is held by bot2
                if other_bot.position == next_pos :
                    # calculates the moving direction of the other bot
                    if other_bot.action.endswith('FORWARD') :
                        moving_dir2 = other_bot.orientation
                    elif other_bot.action.endswith('BACKWARD') :
                        moving_dir2 = (other_bot.orientation + 180) % 360
                    elif other_bot.action.endswith('LEFT') :
                        moving_dir2 = (other_bot.orientation + 90) % 360
                    elif other_bot.action.endswith('RIGHT') :
                        moving_dir2 = (other_bot.orientation - 90) % 360
                    else :
                        raise ValueError("MOVE ??")
                    
                    # if bot2 direction is the opposite of bot1
                    if (moving_dir + 180) % 360 == moving_dir2 :
                        # bot1 won't move to next_pos, it will crash
                        next_pos = bot.position
                        bot.status = 'CRASHED'
                
            if next_pos in destinations :
                destinations[next_pos].append(bot)
            else :
                destinations[next_pos] = [bot]
        
        # computes the crashes happening :
        # when at least 2 bots share the destination
        # when a bot moves (a,b) -> (c,d) and another moves (c,d) -> (a,b) [ * this case is managed before ]
        # when the destination is outside the map or is a wall

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
        shooting_bots = [bot for bot in bots_to_eval if bot.action == 'SHOOT']
        for bot in shooting_bots :

            if bot.orientation == 0 :
                step = (1,0)
            elif bot.orientation == 90 :
                step = (0,1)
            elif bot.orientation == 180 :
                step = (-1,0)
            elif bot.orientation == 270 :
                step = (0,-1)
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
        turning_bots = [bot for bot in bots_to_eval if bot.action.startswith('TURN')]
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
