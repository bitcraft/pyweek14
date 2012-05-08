from lib2d.objects import AvatarObject


class Hero(AvatarObject):
    def __init__(self):
        AvatarObject.__init__(self)
        self.isFalling = False

    def die(self):
        self.avatar.play("die", loop_frame=2) 
