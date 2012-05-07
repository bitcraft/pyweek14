import res
from objects import GameObject
from quadtree import QuadTree, FrozenRect
from pygame import Rect
from bbox import BBox
from pathfinding import astar
from lib2d.signals import *
import math

cardinalDirs = {"north": math.pi*1.5, "east": 0.0, "south": math.pi/2, "west": math.pi}


class CollisionError(Exception):
    pass


class ExitTile(FrozenRect):
    def __init__(self, rect, exit):
        FrozenRect.__init__(self, rect)
        self._value = exit

    def __repr__(self):
        return "<ExitTile ({}, {}, {}, {}): {}>".format(
            self._left,
            self._top,
            self._width,
            self._height,
            self._value)



class AbstractArea(GameObject):
    pass


class Sound(object):
    """
    Class that manages how sounds are played and emitted from the area
    """

    def __init__(self, filename, ttl):
        self.filename = filename
        self.ttl = ttl
        self._done = 0
        self.timer = 0

    def update(self, time):
        if self.timer >= self.ttl:
            self._done = 1
        else:
            self.timer += time

    @property
    def done(self):
        return self._done



class Area(AbstractArea):
    """3D environment for things to live in.
    Includes basic pathfinding, collision detection, among other things.

    uses a quadtree for fast collision testing with level geometry.

    bodies can exits in layers, just like maps.  since the y values can
    vary, when testing for collisions the y value will be truncated and tested
    against the quadtree that is closest.  if there is no quadtree, no
    collision testing will be done.

    there are a few hacks to be aware of:
        bodies move in 3d space, but level geometry is 2d space
        when using pygame rects, the y value maps to the z value in the area

    a word on the coordinate system:
        coordinates are 'right handed'
        x axis moves toward viewer
        y axis move left right
        z axis is height

    Expects to load a specially formatted TMX map created with Tiled.
    Layers:
        Control Tiles
        Upper Partial Tiles
        Lower Partial Tiles
        Lower Full Tiles

    The control layer is where objects and boundries are placed.  It will not
    be rendered.  Your map must not have any spaces that are open.  Each space
    must have a tile in it.  Blank spaces will not be rendered properly and
    will leave annoying trails on the map.

    The control layer must be created with the utility included with lib2d.  It
    contains metadata that lib2d can use to layout and position objects
    correctly.

    REWRITE: FUNCTIONS HERE SHOULD NOT CHANGE STATE

    NOTE: some of the code is specific for maps from the tmxloader
    """


    def defaultPosition(self):
        return BBox(0,0,0,1,1,1)

    def defaultSize(self):
        # TODO: this cannot be hardcoded!
        return (10, 8)


    def __init__(self):
        AbstractArea.__init__(self)
        self.exits    = {}
        self.geometry = {}       # geometry (for collisions) of each layer
        self.bodies = {}         # position and size of bodies in 3d space
        self.orientations = {}   # records where the body is facing
        self.extent = None       # absolute boundries of the area
        self.joins = []          # records simple joins between bodies
        self._oldPositions = {}  # used in collision handling
        self.messages = []
        self.time = 0
        self.tmxdata = None
        self.mappath = None
        self.sounds = []

    def add(self, body):
        AbstractArea.add(self, body)
        self.bodies[body] = self.defaultPosition()
        self.orientations[body] = 0.0


    def movePosition(self, body, (x, y, z), push=False, caller=None, \
                     suppress_warp=False, clip=True):

        """Attempt to move a body in 3d space.

        Args:
            body: (body): body to move
            (x, y, z): difference of position to move
        
        Kwargs:
            push: if True, then any colliding objects will be moved as well
            caller: part of callback for object that created request to move

        Returns:
            None

        Raises:
            CollisionError  


        You should catch the exception if body cannot move.
        This function will emit a bodyRelMove event if successful. 
        """

        movable = 0
        bbox = self.bodies[body].move(x, y, z)

        # collides with level geometry, cannot move
        if self.testCollideGeometry(bbox) and clip:
            return False

        # test for collisions with other bodies
        collide = self.testCollideObjects(bbox)
        try:
            collide.remove(body)
        except:
            pass

        # find things we are joined to
        joins = [ i[1] for i in self.joins if i[0] == body ]

        # if joined, then add it to collisions and treat it is if being pushed
        if joins:
            collide.extend(joins)
            push = True

        # handle collisions with bodies
        if collide:

            # are we pushing something?
            if push and all([ other.pushable for other in collide ]):

                # we are able to move
                originalPosition = self._oldPositions[body]
                self._oldPositions[body] = self.bodies[body]
                self.bodies[body] = bbox

                # recursively push other bodies
                for other in collide:
                    if not self.movePosition(other, (x, y, z), True):
                        # we collided, so just go back to old position
                        self.bodies[body] = self._oldPositions[body]
                        self._oldPositions[body] = originalPosition
                        return False

            else:
                if clip: return False

        self._oldPositions[body] = self.bodies[body]
        self.bodies[body] = bbox

        self._sendBodyMove(body, caller=caller)

        try:
            # emit sounds from bodies walking on them
            tilePos = self.worldToTile(bbox.bottomcenter)
            prop = self.tmxdata.getTileProperties(tilePos)
            if not prop == None:
                name = prop.get('walkSound', None)
                if not name == None:
                    self.emitSound(name, bbox.bottomcenter)
        except:
            pass


        try:
            # test for collisions with exits
            exits = self.exitQT.hit(self.toRect(bbox))
        except AttributeError:
            exits = []


        if exits and not suppress_warp:
            # warp the player
            exit = exits.pop()

            # get the position and guid of the exit tile of the other map
            fromExit, guid = self.exits[exit.value]
            if not guid == None: 
                # used to correctly align sprites
                fromTileBBox = BBox(fromExit, (16,16,1))
                tx, ty, tz = fromTileBBox.origin
            
                # get the GUID of the map we are warping to
                dest = self.getRoot().getChildByGUID(guid)
                toExit, otherExit = dest.exits[exit.value]

                bx, by, bz = bbox.origin
                ox, oy, oz = self._oldPositions[body].origin
                bz = 0

                # determine wich direction we are traveling through the exit
                angle = math.atan2(oy-by, ox-bx)

                # get the position of the tile in out new area
                newx, newy, newz = toExit

                # create a a bbox to position the object in the new area
                dx = 16 / 2 - bbox.depth / 2
                dy = 16 / 2 - bbox.width / 2
                dz = 0
                bbox = BBox((newx+dx, newy+dy, newz+dz), bbox.size)
                face = self.getOrientation(body)
                dest.add(body)
                dest.setBBox(body, bbox)
                dest.setOrientation(body, face)
                

                # when changing the destination, we do a bunch of moves first
                # to push objects out of the way from the door...if possible
                dx = round(math.cos(angle))
                dy = round(math.sin(angle))
                dz = 0
                dest.movePosition(body, (dx*20, dy*20, dz*20), False, \
                                  suppress_warp=True, clip=False)

                for x in range(40):
                    dest.movePosition(body, (-dx, -dy, -dz), True, \
                                      suppress_warp=True, clip=False)

                # send a signal that this body is warping
                bodyWarp.send(sender=self, body=body, destination=dest,
                              caller=caller)

        return True 


    def setOrientation(self, obj, angle):
        """ Set the angle the object is facing.  Expects radians. """

        if isinstance(angle, str):
            try:
                angle = cardinalDirs[angle]
            except:
                raise
        self.orientations[obj] = angle


    def setLayerGeometry(self, layer, rects):
        """
        set the layer's geometry.  expects a list of rects.
        """

        import quadtree

        self.geometry[layer] = quadtree.FastQuadTree(rects)
        self.geoRect = rects


    def pathfind(self, obj, destination):
        """Pathfinding for the world.  Destinations are 'snapped' to tiles.
        """

        def NodeFactory((x, y, l)):
            try:
                if self.tmxdata.getTileGID(x, y, l) == 0:
                    node = Node((x, y))
                else:
                    return None
            except:
                return None
            else:
                return node


        start = self.worldToTile(self.bodies[obj].bottomcenter)
        finish = self._worldToTile((destination[0], destination[1], 0))

        path = astar.search(start, finish, factory)


    def tileToWorld(self, (x, y, z)):
        xx = int(x) * self.tmxdata.tileheight
        yy = int(y) * self.tmxdata.tilewidth
        return xx, yy, z

    def worldToTile(self, (x, y, z)):
        xx = int(y) / self.tmxdata.tileheight
        yy = int(x) / self.tmxdata.tilewidth
        return xx, yy, z

    def pixelToWorld(self, (x, y, z)):
        return (y, x, z)

    def _worldToTile(self, (x, y)):
        return int(y)/self.tmxdata.tileheight, int(x)/self.tmxdata.tilewidth

    def emitSound(self, filename, pos):
        self.sounds = [ s for s in self.sounds if not s.done ]
        if filename not in [ s.filename for s in self.sounds ]:
            emitSound.send(sender=self, filename=filename, position=pos)
            self.sounds.append(Sound(filename, 300))


    def update(self, time):
        self.time += time
        [ sound.update(time) for sound in self.sounds ]
        [ body.update(time) for body in self.bodies ]
        [ self.updatePhysics(body, time) for body in self.bodies ]


    def updatePhysics(self, body, time):
        self.movePosition(body, (0,0,-0.125))


    def setExtent(self, rect):
        self.extent = Rect(rect)


    def testCollideGeometry(self, bbox):
        """
        test if a bbox collides with the layer geometry

        the geometry layer will be calculated from the z value
        """

        # TODO: calc layer value
        layer = 0

        try:
            rect = self.toRect(bbox)
            hit = self.geometry[layer].hit(rect)
            con = self.extent.contains(rect)

            return bool(hit) or not bool(con)

        except KeyError:
            msg = "Area Layer {} does not have a collision layer"
            print msg.format(layer)
            return False

            raise Exception, msg.format(layer)


    def testCollideObjects(self, bbox):
        values = []
        keys = []

        for body, b in self.bodies.items():
            values.append(b)
            keys.append(body)

        return [ keys[i] for i in bbox.collidelistall(values) ]


    def testCollideGeometryAll(self):
        # return list of all collisions between bodies and level geometry
        pass


    def getBBox(self, body):
        """ Return a bbox that represents this body in world """
        return self.bodies[body]


    def setBBox(self, body, bbox):
        """ Attempt to set a bodies bbox.  Returns True if able. """

        if not isinstance(bbox, BBox):
            bbox = BBox(bbox)

        if self.testCollide(bbox):
            return False
        else:
            self.bodies[body] = bbox
            self._oldPositions[body] = bbox
            return True
    

    def testCollide(self, bbox):
        return False


    def getSize(self, body):
        """ Return 3d size of the body """

        return self.bodies[body].size


    def getPositions(self):
        return [ (o, b.origin) for (o, b) in self.bodies.items() ]


    def getOrientation(self, body):
        """ Return the angle body is facing in radians """

        return self.orientations[body]

    # for platformers
    def toRect(self, bbox):
        """
        Make a rect that represents the body's 'bottom plane'.
        """

        return Rect((bbox.y, bbox.z, bbox.width, bbox.height))


    def getOldPosition(self, body):
        return self._oldPositions[body]


    def _sendBodyMove(self, body, caller, force=None):
        position = self.getPosition(body)
        bodyAbsMove.send(sender=self, body=body, position=position, caller=caller, force=force)


    def warpBody(self):
        """
        move a body to another area using an exit tile.
        objects on or around the tile will be push out of the way
        if objects cannot be pushed, then the warp will fail
        """
        pass


    def getPosition(self, body):
        return self.bodies[body].origin


    def stick(self, body):
        self.setPosition(body, self._oldPositions[body])        


    def unstick(self, body):
        pass
