from lib2d.objects import AvatarObject, GameObject
from random import randint


class Laser(GameObject):
    def __init__(self):
        GameObject.__init__(self)
        self.ttl = 60
        self.time = 0

    def update(self, time):
        self.time += time
        if self.time >= self.ttl:
            self.destroy()

    def draw(self, surface):
        surface.fill((255,randint(0,255),255))


class LaserRobot(AvatarObject):
    def __init__(self):
        AvatarObject.__init__(self)
        self.rate = 3000
        self.time = 0
        self.warned = False

    def update(self, time):
        self.time += time
        if self.time >= self.rate:
            self.time -= self.rate
            if self.warned:
                self.warned = False
                self.shoot()
            else:
                self.warned = True
                self.warn()

    def warn(self):
        self.avatar.play("warn", loop=4)

    def shoot(self):
        self.avatar.play("shoot", loop=0)
        laser = Laser()
        self.parent.add(laser)
        self.parent.drawables.append(laser) #hack
        hero = self.parent.getChildByGUID(1)
        if not hero.avatar.isPlaying("crouch"):
            hero.die()
        
