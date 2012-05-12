from lib2d.objects import AvatarObject
from lib.misc import *



fallFlavour = """You leapt before you looked.
You forgot how to levitate.
You left your wings back at base.
The results are in: gravity still exists.
The ground came at you a little to quickly.""".split("\n")



class Hero(AvatarObject):
    def __init__(self):
        AvatarObject.__init__(self)
        self.gravity = True
        self.pushable = True
        self.held = None


    def die(self):
        self.avatar.play("die", loop_frame=2)
        self.isAlive = False


    def fallDamage(self, dmg):
        if dmg > 2:
            self.parent.emitText(choice(fallFlavour), thing=self)
            self.parent.emitText("You are dead.", thing=self)
            self.die()
