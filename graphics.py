
import cocos
from cocos.actions import *

from bots import *

class TitleScreen(cocos.layer.ColorLayer) :
    
    def __init__(self,screen_res) :
        super( TitleScreen, self ).__init__(255,255,255,255)
        
        logo = cocos.sprite.Sprite("imgs/bots.png")
        self.add( logo )
        logo.position = screen_res[0]/2,screen_res[1]/2


class FloorLayer(cocos.layer.ColorLayer) :
    
    sprite_size = 20,20

    def __init__(self,size) :
        super( FloorLayer, self ).__init__(128,128,128,255)

        self.size = size
        self.images = ["imgs/floor.png"]
        self.sprites = {}
        for y in xrange(size[1]) :
            for x in xrange(size[0]) :
                self.sprites[(x,y)] = cocos.sprite.Sprite(self.images[0])
                self.sprites[(x,y)].position = x * self.sprite_size[0] + (self.sprite_size[0]/2),y * self.sprite_size[1] + (self.sprite_size[1]/2)
                self.add( self.sprites[(x,y)] )

class WallLayer(cocos.layer.Layer) :
    
    sprite_size = 20,20

    def __init__(self,arena) :
        super( WallLayer, self ).__init__()
        self.images = ["imgs/wall.png"]
        self.sprites = {}
        for x,y in arena.keys() :
            if arena[(x,y)] == 'WALL' :
                self.sprites[(x,y)] = cocos.sprite.Sprite(self.images[0])
                self.sprites[(x,y)].position = x * self.sprite_size[0] + (self.sprite_size[0]/2),y * self.sprite_size[1] + (self.sprite_size[1]/2)
                self.add( self.sprites[(x,y)] )

class BotLayer(cocos.layer.Layer) :
    
    sprite_size = 20,20
    
    def __init__(self,bots) :
        super( BotLayer, self ).__init__()
        self.images = ["imgs/blue_bot.png"]
        self.sprites = {}
        for b in bots :
            
            self.sprites[(x,y)] = cocos.sprite.Sprite(self.images[0])
            self.sprites[(x,y)].position = x * self.sprite_size[0] + (self.sprite_size[0]/2),y * self.sprite_size[1] + (self.sprite_size[1]/2)
            self.add( self.sprites[(x,y)] )
    



if __name__ == '__main__' :
    screen_res = 800,600
    cocos.director.director.init(screen_res[0],screen_res[1])

    mv = TitleScreen(screen_res)

    x_size,y_size = 40,30

    smap = [[1]*x_size] + [[1] + [0]*(x_size - 2) + [1]]*(y_size - 2) + [[1]*x_size]
    arena = Arena(smap)


    fl = FloorLayer(arena.size)
    wa = WallLayer(arena.map)
    scene = cocos.scene.Scene(fl)
    scene.add(wa)
    
    cocos.director.director.run(scene)
    
