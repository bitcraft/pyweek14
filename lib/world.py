from lib2d.area import AbstractArea, Area
from lib2d.buildarea import fromTMX
from lib2d.avatar import Avatar, Animation, StaticAnimation
from lib2d.objects import AvatarObject
from lib.hero import Hero
from lib.level import Level
from lib.enemies import *
from lib.misc import *
from lib2d import res

from collections import defaultdict
import os, random, types


mootFlavour = \
"""Nothing special seems to happen.
As hard as you try, you just cannot make anything happen.
Nothing.
You lean to to examine it closely, then yawn.  Nothing happens.
I know right, I'm just as bored as you are.  Nothing happens.""".split("\n")

termMootFlavour = \
"""You press a few blinking buttons, but nothing seems to happen.
Click, click, click.  Nothing.
Is this thing even working?
Hitting keys at random has caused nothing to happen.
As you watch the terminal, you wish you were somewhere else.""".split("\n")

print termMootFlavour

def build():

    # build the initial environment
    uni = Area()
    uni.name = 'universe'
    uni.setGUID(0)


    # build our avatars and heros
    avatar = Avatar()
    ani = Animation("hero-idle.png", "stand", 9, 1, 100)
    avatar.add(ani)
    ani = Animation("hero-walk.png", "walk", 10, 1, 80)
    avatar.add(ani)
    ani = Animation("hero-crouch.png", "crouch", 5, 1, 30)
    avatar.add(ani)
    ani = Animation("hero-uncrouch.png", "uncrouch", 5, 1, 30)
    avatar.add(ani)
    ani = Animation("hero-brake.png", "brake", 6, 1, 30)
    avatar.add(ani)
    ani = Animation("hero-run.png", "run", 16, 1, 30)
    avatar.add(ani)
    ani = Animation("hero-sprint.png", "sprint", 17, 1, 100)
    avatar.add(ani)
    ani = Animation("hero-wait.png", "wait", 6, 1, 100)
    avatar.add(ani)
    ani = Animation("hero-jump.png", "jump", 4, 1, 20)
    avatar.add(ani)
    ani = Animation("hero-die.png", "die", 3, 1, 85)
    avatar.add(ani)
    avatar.play("stand")
    npc = Hero()
    npc.setName("Doc")
    npc.setAvatar(avatar)
    npc.setGUID(1)
    npc.size = (4, 16, 32)
    npc.avatar.axis = (-7,0)
    uni.add(npc)


    # laser robot
    avatar = Avatar()
    ani = StaticAnimation("robot-stand.png", "stand")
    avatar.add(ani)
    ani = Animation("robot-shoot.png", "warn", 4, 1, 60)
    avatar.add(ani)
    ani = Animation("robot-shoot.png", "shoot", 4, 1, 30)
    avatar.add(ani)
    npc = LaserRobot()
    npc.setName("LaserRobot")
    npc.setAvatar(avatar)
    npc.setGUID(513)
    npc.size = (2, 14, 30)
    npc.avatar.axis = (-9,-2)
    uni.add(npc)


    # desk
    avatar = Avatar()
    ani = StaticAnimation("desk.png", "idle")
    avatar.add(ani)
    npc = InteractiveObject()
    npc.setName("Desk")
    npc.setAvatar(avatar)
    npc.setGUID(514)
    npc.size = (4, 42, 25)
    npc.avatar.axis = (-2,-6)
    npc.pushable = True
    uni.add(npc)


    # lifts
    avatar = Avatar()
    ani = StaticAnimation("lift-idle.png", "idle")
    avatar.add(ani)
    ani = Animation("lift-glow.png", "glow", 4, 1, 100)
    avatar.add(ani)
    npc = Lift()
    npc.setName("Lift")
    npc.setAvatar(avatar)
    npc.setGUID(769)
    npc.size = (4, 32, 16)
    npc.avatar.axis = (0,16)
    uni.add(npc)

    npc = npc.copy()
    npc.setGUID(770)
    uni.add(npc)

    npc = npc.copy()
    npc.setGUID(771)
    uni.add(npc)

    npc = npc.copy()
    npc.setGUID(772)
    uni.add(npc)

    npc = npc.copy()
    npc.setGUID(773)
    uni.add(npc)


    #lift buttons
    avatar = Avatar()
    ani = StaticAnimation("button2.png", "off")
    avatar.add(ani)
    ani = StaticAnimation("button1.png", "on")
    avatar.add(ani)
    npc = Callbutton()
    npc.setName("Callbutton")
    npc.setAvatar(avatar)
    npc.setGUID(257)
    npc.size = (4, 16, 16)
    uni.add(npc)

    npc = npc.copy()
    npc.setGUID(258)
    uni.add(npc)

    npc = npc.copy()
    npc.setGUID(259)
    uni.add(npc)

    npc = npc.copy()
    npc.setGUID(260)
    uni.add(npc)


    # terminals
    def deadterm(self, user):
        area = user.parent
        area.emitText(random.choice(termMootFlavour), thing=self)
        self.animate()

    def wakebots(self, user):
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

    avatar = Avatar()
    ani = Animation("terminal-idle.png", "idle", 8, 1, 300)
    avatar.add(ani)
    ani = Animation("terminal-glow.png", "glow", 8, 1, 80)
    avatar.add(ani)
    npc = Terminal()
    npc.setName("Terminal")
    npc.setGUID(1281)
    npc.setAvatar(avatar)
    npc.size = (4,16,16)
    npc.use = types.MethodType(deadterm, npc)
    uni.add(npc)

    npc = npc.copy()
    npc.use = types.MethodType(deadterm, npc)
    npc.setGUID(1282)
    uni.add(npc)

    npc = npc.copy()
    npc.use = types.MethodType(wakebots, npc)
    npc.setGUID(1283)
    uni.add(npc)


    # keyed doors
    avatar = Avatar()
    ani = StaticAnimation("door-closed.png", "closed")
    avatar.add(ani)
    ani = StaticAnimation("door-opened.png", "opened")
    avatar.add(ani)
    ani = Animation("door-opening.png", "opening", 8, 1, 30)
    avatar.add(ani)
    ani = Animation("door-closing.png", "closing", 8, 1, 30)
    avatar.add(ani)
    npc = Door()
    npc.setName("Door")
    npc.setGUID(1537)
    npc.setAvatar(avatar)
    npc.size = (10,32,48)
    #npc.forceOff()
    uni.add(npc)


    # load the avatar objects and set their world size based off the first frame
    # of their default animations
    #import pygame, time

    #pygame.init()
    #screen = pygame.display.set_mode((240, 480))
    #pygame.display.set_caption('Image Loading...')

    #for ao in [ i for i in uni.getChildren() if isinstance(i, AvatarObject) ]:
    #    [ i.load() for i in ao.avatar.getChildren() ]
    #    sx, sy = ao.avatar.default.getImage(0).get_size()
    #    x, y, z, d, w, h = ao.parent.getBBox(ao)
    #    ao.parent.setBBox(ao, (x, y, z, 4, sx, sy))
    #    [ i.unload() for i in ao.avatar.getChildren() ]


    # always load the levels last since they may duplicate objects
    level = fromTMX(uni, "start.tmx")
    level.setName("Start")
    level.setGUID(5010)

    level = fromTMX(uni, "level1.tmx")
    level.setName("Level 1")
    level.setGUID(5001)


    #haccckk
    for lift in [ i for i in uni.getChildren() if isinstance(i, Lift) ]:
        body = lift.parent.getBody(lift)
        body.bbox = body.bbox.move(0,0,1)

    pushback = ['Desk']

    for i in [ i for i in uni.getChildren() if i.name in pushback ]:
        body = lift.parent.getBody(i)
        body.bbox = body.bbox.move(-4,0,0)

    return uni
