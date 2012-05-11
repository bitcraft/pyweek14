from lib2d.objects import AvatarObject
from lib.misc import *



class Hero(AvatarObject):
    def __init__(self):
        AvatarObject.__init__(self)
        self.gravity = True
        self.pushable = True
        self.held = None


    def die(self):
        self.avatar.play("die", loop_frame=2)



