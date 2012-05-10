from renderer import LevelCamera

from lib2d.gamestate import GameState
from lib2d.statedriver import driver as sd
from lib2d.buttons import *
from lib2d.signals import *
from lib2d.vec import Vec2d
from lib2d.quadtree import QuadTree, FrozenRect
from lib2d import res, gui
from pytmx import tmxloader

from math import sqrt, atan2
from operator import itemgetter
import pygame
import os.path

import time

debug = 1

movt_fix = 1/sqrt(2)


class SoundManager(object):
    def __init__(self):
        self.sounds = {}
        self.last_played = {}

    def loadSound(self, filename):
        self.sounds[filename] = res.loadSound(filename)
        self.last_played[filename] = 0

    def play(self, filename, volume=1.0):
        now = time.time()
        if self.last_played[filename] + .1 <= now:
            self.last_played[filename] = now
            sound = self.sounds[filename]
            sound.set_volume(volume)
            sound.play()


SoundMan = SoundManager()


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


    def activate(self):
        self.blank = True
        #self.background = (203, 204, 177)
        self.background = (109, 109, 109)
        self.foreground = (0, 0, 0)

        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
        self.player_vector = (0,0,0)
        self.old_player_vector = (0,0,0)
        self.old_falling = None
        self.hero_jump = 35

        # allow the area to get needed data
        self.area.load()

        # get the root and the hero from it
        root = self.area.getRoot()
        self.hero = root.getChildByGUID(1)
        self.hero.move_speed = 16

        # add the hero to this map if it isn't ready there
        if not self.area.hasChild(self.hero):
            self.area.add(self.hero)

        # attach a camera
        sw, sh = sd.get_size()
        mw = sw * .75
        mh = sh * .75
        self.camera = LevelCamera(self.area,((4,4), (mw, mh)),
                                  tmxdata=self.area.tmxdata)

        self.mapBorder = pygame.Rect((0,0,mw+6,mh+6))
        self.msgBorder = pygame.Rect((0,mh,sw,sh-mh))
        self.hudBorder = pygame.Rect((mw,0,sw-mw,mh+6))

        # make a list of elevators in the level
        self.elevators = tmxloader.buildDistributionRects(self.area.tmxdata,
                         "Elevators", gid=None)

        # play music if any has been set in tiled
        try:
            res.playMusic(self.tmxdata.music)
        except AttributeError:
            res.fadeoutMusic()
        
        # load sounds from area
        for filename in self.area.soundFiles:
            SoundMan.loadSound(filename)


    def deactivate(self):
        pass

       
    def drawSidebar(self, surface, rect):
        # draw the static portions of the sidebar
        sw, sh, sw, sh = rect

        self.border.draw(surface, self.hudBorder)
        titleFont = pygame.font.Font(res.fontPath("04b.ttf"), 14)

        i = titleFont.render("PyWeek", 1, (128,128,128))
        surface.blit(i, (sw/2+sw-i.get_size()[0]/2+1, sh+6))

        i = titleFont.render("PyWeek", 1, self.foreground)
        surface.blit(i, (sw/2+sw-i.get_size()[0]/2, sh+5))

        headFont = pygame.font.Font(res.fontPath("volter.ttf"), 9)

        i = headFont.render("Inventory", 1, self.foreground, self.background)
        surface.blit(i, (sw+ 10, sh+30))


    def draw(self, surface):
        sw, sh = surface.get_size()

        if self.blank:
            self.blank = False
            surface.fill(self.background)
            self.drawSidebar(surface, self.hudBorder)
            self.border.draw(surface, self.msgBorder)
            self.camera.blank = True
            dirty = ((0,0), (sw, sh))

        # the main map
        self.camera.center(self.area.getPosition(self.hero))
        dirty = self.camera.draw(surface)

        if self.area.drawables:
            [ o.draw(surface) for o in self.area.drawables ]
            self.blank = True

        # borders
        self.border.draw(surface, self.mapBorder)

        #log = "\n".join(self.area.messages[-5:])
        #rect = self.msgBorder.inflate(-16,-12)
        #gui.drawText(surface, log, (0,0,0), rect, self.msgFont)

        return dirty


    def update(self, time):

        self.area.update(time)
        self.camera.update(time)

        body = self.area.getBody(self.hero)

        # don't move around if not needed
        if (not self.player_vector == self.old_player_vector) or \
           (not body.isFalling == self.old_falling):
            x, y, z = self.player_vector

            # allows you to move in air
            if body.isFalling:
                self.area.setForce(body, (x/3,y/3,z))
            else:
                self.area.setForce(body, (x,y,z))

            # true when idle and grounded
            if (y==0) and (z==0):
                if not body.isFalling:
                    self.hero.avatar.play("stand")

            self.old_player_vector = tuple(self.player_vector)
            self.old_falling = body.isFalling


    # for platformers
    def handle_commandlist(self, cmdlist):
        x = 0
        y = 0
        z = 0

        playing = self.hero.avatar.curAnimation.name

        for cls, cmd, arg in cmdlist:
            if arg == BUTTONUP:
                #if cmd == P1_UP:
                #    self.player_vector.x = 0
                if cmd == P1_DOWN:
                    if playing == "crouch":
                        self.hero.avatar.play("uncrouch", loop=0)

                elif cmd == P1_LEFT:
                    y = 0
                elif cmd == P1_RIGHT:
                    y = 0
                elif cmd == P1_ACTION2:
                    pass

            # these actions will repeat as button is held down
            elif arg == BUTTONDOWN or arg == BUTTONHELD:
                if cmd == P1_UP:
                    self.elevatorUp()

                elif cmd == P1_DOWN:
                    if self.area.grounded(self.area.getBody(self.hero)):
                        if playing == "stand":
                            self.hero.avatar.play("crouch", loop_frame=4)

                    else:
                        self.elevatorDown()

                if cmd == P1_LEFT:
                    y = -1
                    self.hero.avatar.play("run")
                    self.hero.avatar.flip = 1

                elif cmd == P1_RIGHT:
                    y = 1
                    self.hero.avatar.play("run")
                    self.hero.avatar.flip = 0

                if cmd == P1_ACTION2:
                    z = -self.hero_jump


            # these actions will not repeat if button is held
            if arg == BUTTONDOWN:
                if cmd == P1_ACTION1:
                    self.hero.attack()


        self.player_vector = x, y*self.hero.move_speed, z


    def findLift(self, offset):
        body = self.area.getBody(self.hero)
        liftbbox = body.bbox.move(0,0,offset)
        shaftRect = self.area.toRect(body.bbox.move(0,0,-body.bbox.height))

        for rect in self.elevators:
            if rect.colliderect(shaftRect):
                l = self.area.testCollideObjects(liftbbox)
                l.remove(body)
                if l:
                    lift = l.pop()
                    return lift

        return None


    def elevatorUp(self):
        lift = self.findLift(3)

        if lift:
            body = self.area.getBody(self.hero)
            self.area.movePosition(body, (0,0,-2), push=False)
            self.area.movePosition(lift, (0,0,-2), push=True)
            lift.parent.animate()


    def elevatorDown(self):
        lift = self.findLift(1)

        if lift:
            body = self.area.getBody(self.hero)
            self.area.movePosition(lift, (0,0,2), push=True)
            self.area.movePosition(body, (0,0,2), push=False)
            lift.parent.animate()


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


