from lib2d.objects import InteractiveObject, GameObject
from lib2d.avatar import Animation
from lib2d import res
from random import randint, choice

from lib.enemies import *


text = {}
text['take'] = "You take a {} from {}"

termMootFlavour = \
"""You press a few blinking buttons, but nothing seems to happen.
Click, click, click.  Nothing.
Is this thing even working?
Hitting keys at random has caused nothing to happen.
As you watch the terminal, you wish you were somewhere else.""".split("\n")


class InventoryObject(InteractiveObject):
    """
    holds stuff
    """

    def use(self, user):
        for i in self.inventory:
            user.parent.emitText(text['take'].format(i.name, self.name), thing=self)
            self.removeThing(i)
            user.addThing(i)


class Lift(InteractiveObject):
    sounds = ["lift.wav"]
    gravity = False

    def __init__(self):
        InteractiveObject.__init__(self)
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


class Callbutton(InteractiveObject):
    sounds = ['pushbutton.wav']
    gravity = False
    resetDelay = 300

    def __init__(self):
        InteractiveObject.__init__(self)
        self.state = 0
        self.time = 0


    def use(self, user=None):
        self.on()
        body = self.parent.getBody(self)
        lift = self.parent.getChildByGUID(self.liftGUID) 
        lift.call(body.bbox.top, caller=self)


    def update(self, time):
        if not self.state == 2: return

        self.time += time
        if self.time >= self.resetDelay:
            self.forceOff()
            self.time = 0


    def forceOff(self):
        self.avatar.play("off")
        self.state = 0


    def off(self):
        self.state = 2


    def on(self):
        self.state = 1
        self.parent.emitSound("pushbutton.wav", thing=self)
        self.avatar.play("on")


class Key(InteractiveObject):
    pass


class Terminal(InteractiveObject):
    sounds = ['terminal.wav']
    gravity = False
    activated = False


    def use(self, user=None):
        self.animate()

    def animate(self):
        self.avatar.play('glow', loop=2)
        self.parent.emitSound("terminal.wav", thing=self)


class WakeTerminal(Terminal):
    def use(self, user):
        area = user.parent
        if self.activated:
            area.emitText("Your face is still throbbing from when you last hit the terminal with it.", thing=self)

        else:
            self.activated = True
            bots = [ i for i in self.parent.getChildren() if isinstance(i, LaserRobot) ]
            for bot in bots:
                bot.activate()
            area.emitText("Surprisingly, hitting your face against the keypad seemed to do something.", thing=self)

        self.animate()

class DeadTerminal(Terminal):
    def use(self, user):
        area = user.parent
        area.emitText(choice(termMootFlavour), thing=self)
        self.animate()




class Door(InteractiveObject):
    sounds = ['door-open.wav', 'door-close.wav']
    pushable = False


    def __init__(self):
        InteractiveObject.__init__(self)
        self.state = 0
        self.key = None


    def use(self, user=None):
        if self.key and user:
            if self.key in [ i for i in user.getChildren() ]:
                self.toggle(user)
            else:
                return
        else:
            self.toggle(user)


    def toggle(self, user=None):
        if self.state:
            if user:
                body0 = self.parent.getBody(self)
                body1 = self.parent.getBody(user)
                if not (body0 in self.parent.testCollideObjects(body1.bbox)):
                    self.off()
            else:
                self.off()
        else:
            self.on()


    def forceOff(self):
        self.avatar.play("closed")
        self.state = 0
        body = self.parent.getBody(self)
        body.bbox = body.bbox.move(16,0,0)


    def forceOn(self):
        self.avatar.play("opened")
        self.state = 3
        body = self.parent.getBody(self)
        body.bbox = body.bbox.move(-16,0,0)


    def off(self):
        self.parent.emitSound("door-close.wav", thing=self)
        self.avatar.play("closing", loop=0, callback=self.forceOff)
        self.state = 2


    def on(self):
        self.parent.emitSound("door-open.wav", thing=self)
        self.avatar.play("opening", loop=0, callback=self.forceOn)
        self.state = 1
