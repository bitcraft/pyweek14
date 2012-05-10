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
import os



# build the initial environment
uni = Area()
uni.name = 'MH'
uni.setGUID(0)


# build our avatars and heros
avatar = Avatar()
ani = Animation("hero-idle.png", "stand", 9, 1, 100)
avatar.add(ani)
ani = Animation("hero-walk.png", "walk", 10, 1, 100)
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
npc.size = (4, 14, 32)
npc.avatar.axis = (-9,0)
uni.add(npc)


# lifts
avatar = Avatar()
ani = StaticAnimation("lift-idle.png", "idle")
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
level = fromTMX(uni, "level1.tmx")
level.setName("Level 1")
level.setGUID(1001)


uni.save(os.path.join("resources", "worlds", "world"))
#pygame.quit()
