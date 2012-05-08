from lib2d.objects import AvatarObject


class Hero(AvatarObject):
    def __init__(self):
        AvatarObject.__init__(self)
        self.isFalling = False
        
