from lib2d.area import AbstractArea, Area
from lib2d.buildarea import fromTMX
from lib2d.avatar import Avatar, Animation, StaticAnimation
from lib2d.objects import AvatarObject
from lib2d import res, tmxloader
from lib.hero import Hero
from lib.level import Level

from collections import defaultdict
import os



# build the initial environment
uni = AbstractArea()
uni.name = 'MH'
uni.setGUID(0)

# build our avatars and heros
avatar = Avatar()
ani = Animation("idle.png", "stand", 9, 1, 100)
avatar.add(ani)
ani = Animation("walk.png", "walk", 10, 1, 100)
avatar.add(ani)
ani = Animation("crouch.png", "crouch", 5, 1, 30)
avatar.add(ani)
ani = Animation("brake.png", "brake", 6, 1, 30)
avatar.add(ani)
ani = Animation("run.png", "run", 16, 1, 50)
avatar.add(ani)
ani = Animation("sprint.png", "sprint", 17, 1, 100)
avatar.add(ani)
ani = Animation("wait.png", "wait", 6, 1, 100)
avatar.add(ani)
avatar.play("stand")
npc = Hero()
npc.setName("Doc")
npc.setAvatar(avatar)
npc.setGUID(1)
uni.add(npc)


village = fromTMX(uni, "level1.tmx")
village.setName("Level 1")
village.setGUID(1001)


uni.save(os.path.join("resources", "worlds", "world"))

