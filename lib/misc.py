from lib2d.objects import AvatarObject, GameObject
from lib2d.avatar import Animation, Avatar
from lib2d import res
from random import randint



class Lift(AvatarObject):
    sounds = ["lift.wav"]

    def __init__(self):
        AvatarObject.__init__(self)
        self.gravity = False
        self.direction = 0
        self.caller = None
        self.destination = None


    def animate(self):
        self.avatar.play("glow", loop=1)
        self.parent.emitSound("lift.wav", ttl=1000, thing=self) 


    def update(self, time):
        if self.destination:
            body = self.parent.getBody(self)
            self.parent.movePosition(body, (0,0,self.direction), clip=False)
            self.animate()
            bottom = int(body.bbox.bottom)
            if bottom == self.destination:
                d = self.destination - body.bbox.bottom
                self.parent.movePosition(body, (0,0,d))
                self.cancelCall()


    def cancelCall(self):
        if self.caller: 
            self.caller.off()

        self.destination = None
        self.caller = None
        self.direction = None


    def call(self, dest, caller=None):
        bbox = self.parent.getBody(self).bbox
        if dest > bbox.bottom:
            self.caller = caller
            self.destination = int(dest)
            self.direction = 1
        elif dest < bbox.bottom:
            self.caller = caller
            self.destination = int(dest)
            self.direction = -1
        elif caller:
            caller.off() 


class Callbutton(AvatarObject):
    sounds = ['pushbutton.wav']


    def use(self):
        self.on()
        body = self.parent.getBody(self)
        lift = self.parent.getChildByGUID(self.liftGUID) 
        lift.call(body.bbox.top, caller=self)


    def off(self):
        self.avatar.play("off")


    def on(self):
        self.parent.emitSound("pushbutton.wav", thing=self)
        self.avatar.play("on")


class Key(AvatarObject):
    pass
