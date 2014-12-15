import cocos
from cocos.actions import *
import pyglet


class BotSprite(cocos.sprite.Sprite) :
    
    def __init__(self,image,orientation) :
        super( BotSprite, self ).__init__(image)
        self.busy = True
        self.do ( RotateBy(-orientation,0.0) + CallFunc(self.free) )

    def free(self) :
        self.busy = False

    def die(self) :
        self.do(Hide())
        self.kill()

class Laser(cocos.sprite.Sprite) :
    
    def __init__(self,image,from_pos,to_pos,time) :
        super( Laser, self ).__init__(image)
        self.position = from_pos

        # schedules the destruction of the sprite 1s after the animation
        self.schedule_interval(self.done_animation,time + 1)
        self.do(MoveTo(to_pos,time) | FadeOut(time))

    def done_animation(self,timedelta):
        self.kill()
        
        

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
