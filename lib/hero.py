from lib2d.objects import AvatarObject


class Hero(AvatarObject):
    def __init__(self):
        AvatarObject.__init__(self)
        self.gravity = True


    def die(self):
        self.avatar.play("die", loop_frame=2)


    def use(self):
        # attempt to use something in the environment

        body = self.parent.getBody(self)
        bbox = body.bbox.inflate(2,2,2)

        print self.parent.testCollideObjects(bbox)
