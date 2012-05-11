from lib2d.objects import AvatarObject
from lib.misc import *


def getNearby(thing, d):
    body = thing.parent.getBody(thing)
    bbox = body.bbox.inflate(d,d,d)

    l = thing.parent.testCollideObjects(bbox)
    l.remove(body)

    if l:
        return l.pop().parent
    else:
        return None


class Hero(AvatarObject):
    def __init__(self):
        AvatarObject.__init__(self)
        self.gravity = True
        self.pushable = True


    def die(self):
        self.avatar.play("die", loop_frame=2)


    def use(self):
        # attempt to use something in the environment

        other = getNearby(self, 2)
        if not other:
            return
        
        if hasattr(other, "use"):
            other.use(self)

