from time import sleep 
import cocos
from cocos.actions import *
from sprites import *

from bots import *

class TitleScreen(cocos.scene.Scene) :
    
    def __init__(self,screen_res) :
        super( TitleScreen, self ).__init__()

        bgLayer = cocos.layer.ColorLayer(255,255,255,255)
        logo = cocos.sprite.Sprite("imgs/bots.png")
        logo.position = screen_res[0]/2,screen_res[1]/2
        bgLayer.add( logo )

        self.add( bgLayer )

class GameScreen(cocos.scene.Scene) :
    
    tile_size = 20,20
    move_time = 0.4
    turn_time = 0.4

    def __init__(self,game) :

        super( GameScreen, self ).__init__()

        self.game = game
        
        # loads the resources
        self.loadResources()
        
        self.drawTerrain()
        self.drawBots()

        # schedules updates
        self.schedule(self.update)
        

        # adds the layers to the scene
        self.add(self.floorLayer)
        self.add(self.wallLayer)
        self.add(self.botLayer)

    def loadResources(self) :

        imageFolder = 'imgs/'
        
        # loads terrain images
        self.floorImage = imageFolder + 'floor.png'
        self.wallImage = imageFolder + 'wall.png'

        # loads bot images
        self.botImages = {}
        image_prefixes = ['blue','green','purple','yellow']
        for i,player in enumerate(self.game.players) :
            self.botImages[player] = imageFolder + '{}_bot.png'.format(image_prefixes[i])

        self.laserImages = []
        for orient in [0,90,180,270] :
            self.laserImages.append(imageFolder + 'laser_{}.png'.format(str(orient)))

    def drawTerrain(self) :

        # draws the floor..
        self.floorLayer = cocos.layer.ColorLayer(128,128,128,255)
        self.floorLayer.sprites = {}
        ts = self.tile_size
        for y in xrange(self.game.arena.size[1]) :
            for x in xrange(self.game.arena.size[0]) :
                self.floorLayer.sprites[(x,y)] = cocos.sprite.Sprite(self.floorImage)
                self.floorLayer.sprites[(x,y)].position = x * ts[0] + (ts[0]/2),y * ts[1] + (ts[1]/2)
                self.floorLayer.add( self.floorLayer.sprites[(x,y)] )

        # ..and the walls
        self.wallLayer = cocos.layer.Layer()
        self.wallLayer.sprites = {}
        for x,y in self.game.arena.map.keys() :
            if self.game.arena.map[(x,y)] == 'WALL' :
                self.wallLayer.sprites[(x,y)] = cocos.sprite.Sprite(self.wallImage)
                self.wallLayer.sprites[(x,y)].position = x * ts[0] + (ts[0]/2),y * ts[1] + (ts[1]/2)
                self.wallLayer.add( self.wallLayer.sprites[(x,y)] )

    def drawBots(self) :
        
        self.botLayer = cocos.layer.Layer()
        
        self.botLayer.sprites = {}
        ts = self.tile_size
        for i,bot in enumerate(self.game.bots) :
            self.botLayer.sprites[i] = BotSprite( self.botImages[bot.player], bot.orientation )
            self.botLayer.sprites[i].position = ts[0] * bot.position[0] + ts[0] / 2, ts[1] * bot.position[1] + ts[1] / 2

            self.botLayer.add( self.botLayer.sprites[i] )


    def update(self,timedelta) :

        if len([sprite for sprite in self.botLayer.sprites.values() if sprite.busy == True]) > 0 :
            return

        self.game.turn()

        ts = self.tile_size
        for i,bs in self.botLayer.sprites.items() :
            # updates just the operative bots
            if self.game.bots[i].status == 'OPERATIVE' :
                bs.busy = True
                if self.game.bots[i].action.startswith('MOVE') :
                    x = self.game.bots[i].position[0] * ts[0] + ts[0]/2
                    y = self.game.bots[i].position[1] * ts[1] + ts[1]/2
                    bs.do ( MoveTo((x,y),self.move_time) + cocos.actions.CallFunc( bs.free ))
                elif self.game.bots[i].action == 'TURN LEFT' :
                    bs.do ( RotateBy(-90,self.turn_time) + cocos.actions.CallFunc( bs.free ))
                elif self.game.bots[i].action == 'TURN RIGHT' :
                    bs.do ( RotateBy(90,self.turn_time) + cocos.actions.CallFunc( bs.free ))
                elif self.game.bots[i].action == 'SHOOT' :
                    from_pos = self.game.bots[i].position[0] * ts[0] + ts[0]/2, self.game.bots[i].position[1] * ts[1] + ts[1]/2
                    to_pos = list(from_pos)
                    if self.game.bots[i].orientation == 0 :
                        to_pos[0] += self.game.bots[i].fire_range * ts[0]
                    elif self.game.bots[i].orientation == 90 :
                        to_pos[1] += self.game.bots[i].fire_range * ts[1]
                    elif self.game.bots[i].orientation == 180 :
                        to_pos[0] -= self.game.bots[i].fire_range * ts[0]
                    elif self.game.bots[i].orientation == 270 :
                        to_pos[1] -= self.game.bots[i].fire_range * ts[1]
                    lim = self.laserImages[ self.game.bots[i].orientation / 90 ]
                    self.botLayer.add( Laser(lim,from_pos,to_pos) )

                    bs.busy = False
                else :
                    bs.busy = False
            if self.game.bots[i].status == 'HIT' or self.game.bots[i].status == 'CRASHED' :
                x = self.game.bots[i].position[0] * ts[0] + ts[0]/2
                y = self.game.bots[i].position[1] * ts[1] + ts[1]/2
                self.botLayer.add( Explosion((x,y)) )
                bs.die()
                self.botLayer.sprites.pop(i)
                

    

if __name__ == '__main__' :
    screen_res = 800,600
    cocos.director.director.init(screen_res[0],screen_res[1])

    mv = TitleScreen(screen_res)

    x_size,y_size = 20,20
    smap = [[1]*x_size] + [[1] + [0]*(x_size - 2) + [1]]*(y_size - 2) + [[1]*x_size]
    arena = Arena(smap)


    fl = FloorLayer(arena.size)
    wa = WallLayer(arena.map)
    scene = cocos.scene.Scene(fl)
    scene.add(wa)
    
    cocos.director.director.run(mv)
    


