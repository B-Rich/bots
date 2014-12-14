import cocos
from cocos.actions import *
import pyglet


class BotSprite(cocos.sprite.Sprite) :
    
    def __init__(self,image) :
        super( BotSprite, self ).__init__(image)
        self.busy = False

    def free(self) :
        self.busy = False

    def die(self) :
        self.do(Hide())



class Explosion(cocos.sprite.Sprite):
    animation = None
    bin = None

    def pre_init(self):
        Explosion.animation = pyglet.image.load_animation('imgs/explosion.gif')
        Explosion.bin = pyglet.image.atlas.TextureBin()
        Explosion.animation.add_to_texture_bin(Explosion.bin)

    def __init__(self, position) :
        if not Explosion.animation: self.pre_init()
        super(Explosion, self).__init__(Explosion.animation)
        self.position = position
        self.scale = 1
        self.schedule_interval(self.done_animation,0.5)
        self.do(FadeOut(0.4))

    def done_animation(self,timedelta):
        self.kill()
