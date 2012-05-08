from renderer import LevelCamera

from lib2d.gamestate import GameState
from lib2d.statedriver import driver as sd
from lib2d.buttons import *
from lib2d.signals import *
from lib2d.vec import Vec2d
from lib2d.quadtree import QuadTree, FrozenRect
from lib2d import tmxloader, res, gui

from math import sqrt, atan2
from operator import itemgetter
import pygame
import os.path

debug = 1

movt_fix = 1/sqrt(2)


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

class ControllerHandler(object):
    """
    Some kind of glue between the input of the player and the actions
    he is allowed to make.  New territory here.
    """

    def __init__(self, controller, model):
        self.model = model


    def getActions(self):
        """
        Return a list of actions the character is allowed to make at the
        moment
        """

        pass


class LevelState(GameState):
    """
    This state is where the player will move the hero around the map
    interacting with npcs, other players, objects, etc.

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

    i would really like the game to be sandboxable...set traps,
    make contraptions, etc

    controls:
        picking up objects will affect what your buttons do
        equipted items always have a dedicated button
        should have hot-swap button and drop button
    """

    def __init__(self, area, startPosition=None):
        GameState.__init__(self)
        self.area = area
        self.heroOnExit = False         # use this flag when warping
        self.background = (203, 204, 177)
        self.foreground = (0, 0, 0)
        self.blank = True


    def activate(self):
        self.sounds = {}

        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
        self.player_vector = (0,0,0)
        self.old_player_vector = (0,0,0)
        self.hero_jump = 27

        # get the root and the hero from it
        root = self.area.getRoot()
        self.hero = root.getChildByGUID(1)
        self.hero.move_speed = 16

        # add the hero to this map if it isn't ready there
        if not self.area.hasChild(self.hero):
            self.area.add(self.hero)

        # load the tmx data here.  it will be shared with the camera.
        self.tmxdata = tmxloader.load_pygame(
                       self.area.mappath, force_colorkey=(128,128,0))

        # attach a camera
        sw, sh = sd.get_size()
        mw = sw * .75
        mh = sh * .75
        self.camera = LevelCamera(self.area,((4,4), (mw, mh)),
                                  tmxdata=self.tmxdata)

        self.mapBorder = pygame.Rect((0,0,mw+6,mh+6))
        self.msgBorder = pygame.Rect((0,mh,sw,sh-mh))
        self.hudBorder = pygame.Rect((mw,0,sw-mw,mh+6))


        # play music if any has been set in tiled
        try:
            res.playMusic(self.tmxdata.music)
        except AttributeError:
            res.fadeoutMusic()
            
        # quadtree for handling collisions with exit tiles
        rects = []
        for guid, param in self.area.exits.items():
            try:
                x, y, l = param[0]
            except:
                continue
            rects.append(ExitTile((x,y,
                self.tmxdata.tilewidth, self.tmxdata.tileheight),
                guid))

        #self.exitQT = QuadTree(rects)

        # load tile sounds
        for i, layer in enumerate(self.tmxdata.tilelayers):
            props = self.tmxdata.getTilePropertiesByLayer(i)
            for gid, tileProp in props:
                for key, value in tileProp.items():
                    if key[4:].lower() == "sound":
                        self.sounds[value] = res.loadSound(value)


    def deactivate(self):
        pass

       
    def drawSidebar(self, surface, rect):
        # draw the static portions of the sidebar
        sx, sy, sw, sh = rect

        self.border.draw(surface, self.hudBorder)
        titleFont = pygame.font.Font(res.fontPath("04b.ttf"), 14)

        i = titleFont.render("PyWeek", 1, (128,128,128))
        surface.blit(i, (sw/2+sx-i.get_size()[0]/2+1, sy+6))

        i = titleFont.render("PyWeek", 1, self.foreground)
        surface.blit(i, (sw/2+sx-i.get_size()[0]/2, sy+5))

        headFont = pygame.font.Font(res.fontPath("volter.ttf"), 9)

        i = headFont.render("Inventory", 1, self.foreground, self.background)
        surface.blit(i, (sx+ 10, sy+30))


    def draw(self, surface):
        sx, sy = surface.get_size()

        if self.blank:
            self.blank = False
            surface.fill(self.background)
            self.drawSidebar(surface, self.hudBorder)

        # the main map
        self.camera.center(self.area.getPosition(self.hero))
        self.camera.draw(surface)

        if self.area.drawables:
            [ o.draw(surface) for o in self.area.drawables ]
            self.blank = True

        # borders
        #self.borderFilled.draw(surface, self.msgBorder)
        self.border.draw(surface, self.mapBorder)

        #log = "\n".join(self.area.messages[-5:])
        #rect = self.msgBorder.inflate(-16,-12)
        #gui.drawText(surface, log, (0,0,0), rect, self.msgFont)


        return


    def update(self, time):

        self.area.update(time)
        self.camera.update(time)

        g = self.area.grounded(self.hero)

        # true when landing after a fall
        if self.hero.isFalling and g:
            self.hero.isFalling = False
            self.area.setForce(self.hero, self.player_vector)
            self.hero.avatar.play("stand")

        # don't move around if not needed
        if not self.player_vector == self.old_player_vector:
            x, y, z = self.player_vector

            g = self.area.grounded(self.hero)
            if g:
                if self.hero.isFalling:
                    self.hero.isFalling = False

                self.area.setForce(self.hero, (x,y,0))

                if not self.hero.avatar.isPlaying("crouch"):
                    self.area.applyForce(self.hero, (0,0,z))

            # true when not grounded and letting go of controls
            elif x==y==0:
                self.hero.isFalling = True

            # true when idle and grounded
            if y==0 and z==0 and not self.hero.isFalling:
                self.hero.avatar.play("stand")

            # true when beginning to jump
            elif not y==0 and not z==0:
                pass

            # true when moving and not jumping
            elif not z:
                self.hero.avatar.play("run")
            
            self.old_player_vector = tuple(self.player_vector)


    # for platformers
    def handle_commandlist(self, cmdlist):
        x = 0
        y = 0
        z = 0

        for cls, cmd, arg in cmdlist:
            if arg == BUTTONUP:
                #if cmd == P1_UP:
                #    self.player_vector.x = 0
                if cmd == P1_DOWN:
                    if self.hero.avatar.isPlaying("crouch"):
                        self.hero.avatar.play("uncrouch", loop=0)
                elif cmd == P1_LEFT:
                    y = 0
                elif cmd == P1_RIGHT:
                    y = 0
                elif cmd == P1_ACTION2:
                    pass

            # these actions will repeat as button is held down
            elif arg == BUTTONDOWN or arg == BUTTONHELD:
                #if   cmd == P1_UP:      x = -1
                #elif cmd == P1_DOWN:    x = 1
                if cmd == P1_LEFT:
                    y = -1
                    self.hero.avatar.flip = 1

                elif cmd == P1_RIGHT:
                    y = 1
                    self.hero.avatar.flip = 0
                elif cmd == P1_ACTION2:
                    z = -self.hero_jump

            # these actions will not repeat if button is held
            if arg == BUTTONDOWN:
                if cmd == P1_ACTION1:
                    self.hero.attack()

                elif cmd == P1_DOWN:
                    if self.area.grounded(self.hero):
                        self.hero.avatar.play("crouch", loop_frame=4)

            # don't rotate the player if he's grabbing something
            #if not self.hero.arms == GRAB:
            #    self.area.setOrientation(self.hero, atan2(x, y))

        self.player_vector = x, y*self.hero.move_speed, z

@receiver(emitSound)
def playSound(sender, **kwargs):
    SoundMan.play(kwargs['filename'])


@receiver(bodyAbsMove)
def bodyMove(sender, **kwargs):
    area = sender
    body = kwargs['body']
    position = kwargs['position']
    state = kwargs['caller']

    if state == None:
        return

    if body == state.hero:
        state.camera.center(position)


@receiver(bodyWarp)
def bodyWarp(sender, **kwargs):
    area = sender
    body = kwargs['body']
    destination = kwargs['destination']
    state = kwargs['caller']

    if state == None:
        return

    if body == state.hero:
        sd.push(WorldState(destination))
        sd.done()


