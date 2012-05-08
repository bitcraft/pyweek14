from lib2d.area import AbstractArea, Area
from lib2d.buildarea import fromTMX
from lib2d.avatar import Avatar, Animation, StaticAnimation
from lib2d.objects import AvatarObject
from lib2d import res, tmxloader
from lib.hero import Hero
from lib.level import Level
from lib.enemies import *

from collections import defaultdict
import os



# build the initial environment
uni = AbstractArea()
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
uni.add(npc)


village = fromTMX(uni, "level1.tmx")
village.setName("Level 1")
village.setGUID(1001)


uni.save(os.path.join("resources", "worlds", "world"))

