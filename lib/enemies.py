from lib2d.objects import AvatarObject, GameObject
from lib2d.avatar import Animation, Avatar
from lib2d import res
from random import randint

import gc



class Laser(GameObject):
    def __init__(self):
        GameObject.__init__(self)
        self.ttl = 60
        self.time = 0

    def update(self, time):
        self.time += time
        if self.time >= self.ttl:
            self.destroy()
        self.parent.flash = self.parent.getBody(self).bbox.center


class LaserRobot(AvatarObject):
    sounds = ["ex0.wav", "warn.wav", "whiz0.wav"]

    def __init__(self):
        AvatarObject.__init__(self)
        self.rate = 3000
        self.time = 0
        self.warned = False
        self.pushable = True
        self.activated = False


    def activate(self):
        self.activated = True
        self.parent.emitSound("whiz0.wav", thing=self)


    def update(self, time):
        if not self.activated: return

        self.time += time
        if self.time >= self.rate:
            self.time -= self.rate
            if self.warned:
                self.warned = False
                self.shoot()
            else:
                self.warned = True
                self.warn()

        if self.isFalling and self.isAlive:
            self.isAlive = False
            self.die()


    def die(self):
        def destroy():
            body0 = self.parent.getBody(self)
            body1 = self.parent.getBody(bolt)
            self.parent.unjoin(body0, body1)
            bolt.destroy()
            #self.destroy()

        bolt = AvatarObject()
        bolt.name = "bolt"
        avatar = Avatar()
        ani = Animation("electrify.png", "electrify", 2, 1, 50)
        avatar.add(ani)
        avatar.play("electrify", loop=3, callback=destroy)
        bolt.setAvatar(avatar)
        self.parent.add(bolt)
        x, y, z, d, w, h = self.parent.getPosition(self)
        self.parent.setPosition(bolt, (x, y, z, 10, w, h))
        body0 = self.parent.getBody(self)
        body1 = self.parent.getBody(bolt)
        self.parent.join(body0, body1)
        ani.load()


    def warn(self):
        self.avatar.play("warn", loop=4)
        self.parent.emitSound("warn.wav", thing=self)
        self.parent.emitText("A robot charges his laser.", thing=self)


    def shoot(self):
        self.avatar.play("shoot", loop=0)
        laser = Laser()
        self.parent.add(laser)
        hero = self.parent.getChildByGUID(1)
        if not hero.avatar.isPlaying("crouch"):
            hero.die()
        
        self.parent.emitSound("ex0.wav", thing=self)
