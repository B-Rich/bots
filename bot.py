from random import randint

class Bot :
    def __init__(self,program,player,game=None,position=None,orientation=None,FOV=2,fire_range=4) :
        self.program = program
        self.player = player
        self.game = game
        self.position = position
        self.orientation = orientation
        self.FOV = FOV
        self.fire_range = fire_range


class EvalBot(Bot) :
    
    def __init__(self,program,player,game=None,position=None,orientation=None,FOV=2,fire_range=4) :

        Bot.__init__(self,program,player,game,position,orientation,FOV,fire_range)
        self.status = 'OPERATIVE'
        self.action = 'WAIT'

        self.coinflip = None
        self.dice = None

    def sensor(self,x,y) :
        if x > self.FOV or y > self.FOV :
            raise BotException("out of FOV")        
        
        if self.orientation == 0 :
            bias = x,y
        elif self.orientation == 90 :
            bias = y,-x
        elif self.orientation == 180 :
            bias = -x,-y
        elif self.orientation == 270 :
            bias = -y,x

        abs_pos = (self.position[0] + bias[0],self.position[1] + bias[1])
        if abs_pos[0] < 0 or abs_pos[1] < 0 or abs_pos[0] >= self.game.arena.size[0] or abs_pos[1] >= self.game.arena.size[1] :
            return 'WALL'
        if self.game.arena.map[abs_pos] != 'WALL' :
            retStr = 'FLOOR'
            for bot in self.game.bots :
                if bot.position == abs_pos and bot.status == 'OPERATIVE' :
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













