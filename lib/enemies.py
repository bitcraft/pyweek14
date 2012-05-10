from lib2d.objects import AvatarObject, GameObject
from lib2d.avatar import Animation, Avatar
from lib2d import res
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
            pass

    def draw(self, surface):
        surface.fill((255,randint(0,255),255))


class LaserRobot(AvatarObject):
    def __init__(self):
        AvatarObject.__init__(self)
        self.rate = 3000
        self.time = 0
        self.warned = False
        self.pushable = True


    def load(self):
        self.shootSound = res.loadSound("ex0.wav")
        self.warnSound = res.loadSound("warn.wav")


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

        if self.isFalling and self.isAlive:
            self.isAlive = False
            self.die()


    def die(self):
        print "die"
        bolt = AvatarObject()
        avatar = Avatar()
        ani = Animation("electrify.png", "electrify", 2, 1, 50)
        ani.load()
        avatar.add(ani)
        avatar.play("electrify", loop=3, callback=bolt.destroy)
        bolt.setAvatar(avatar)
        self.parent.add(bolt)
        self.parent.setPosition(bolt, self.parent.getPosition(self))


    def warn(self):
        self.avatar.play("warn", loop=4)
        self.warnSound.play()


    def shoot(self):
        self.avatar.play("shoot", loop=0)
        laser = Laser()
        self.parent.add(laser)
        self.parent.drawables.append(laser) #hack
        hero = self.parent.getChildByGUID(1)
        if not hero.avatar.isPlaying("crouch"):
            hero.die()
        
        self.shootSound.play()
