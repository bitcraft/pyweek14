from renderer import LevelCamera

from lib2d.gamestate import GameState
from lib2d.statedriver import driver as sd
from lib2d.buttons import *
from lib2d.signals import *
from lib2d.vec import Vec2d
from lib2d.quadtree import QuadTree, FrozenRect
from lib2d import res, gui
from pytmx import tmxloader

from random import randint
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

    def unload(self):
        self.sounds = {}
        self.last_played = {}


SoundMan = SoundManager()


# GLOBAL LEET SKILLS
heroBody = None
state = None


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

    """

    def __init__(self, area, startPosition=None):
        GameState.__init__(self)
        self.area = area
        global state
        state = self

    def activate(self):
        global hero_body

        self.blank = True
        self.background = (109, 109, 109)
        self.foreground = (0, 0, 0)

        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
        self.player_vector = (0,0,0)
        self.old_player_vector = (0,0,0)
        self.old_falling = None
        self.hero_jump = 25

        self.music_pos = 0.0

        self.updateText = False
        self.messages = []

        self.camera = None

        # allow the area to get needed data
        self.area.load()

        # load the children
        for child in self.area.getChildren():
            child.load()

        # get the root and the hero from it
        root = self.area.getRoot()
        self.hero = root.getChildByGUID(1)
        self.hero.move_speed = 16

        # add the hero to this map if it isn't ready there
        if not self.area.hasChild(self.hero):
            self.area.add(self.hero)

        hero_body = self.area.getBody(self.hero)

        # make a list of elevators in the level
        self.elevators = tmxloader.buildDistributionRects(self.area.tmxdata,
                         "Elevators", gid=None)

        # load sounds from area
        for filename in self.area.soundFiles:
            SoundMan.loadSound(filename)

        self.reactivate()


    def deactivate(self):
        res.fadeoutMusic(1000)
        # unload the children
        for child in self.area.getChildren():
            child.unload()
        self.area.music_pos = float(pygame.mixer.music.get_pos()) / 1000
        SoundMan.unload()   

 
    def reactivate(self):
        # play music if any has been set in tiled
        try:
            res.playMusic(self.area.tmxdata.music, start=self.area.music_pos)
        except AttributeError:
            res.fadeoutMusic()
            self.music_playing = False 
        else:
            self.music_playing = True    

       
    def drawInfobar(self, surface, rect):
        # draw the static portions of the sidebar
        sw, sh, sw, sh = rect

        self.border.draw(surface, self.hudBorder)
        titleFont = pygame.font.Font(res.fontPath("04b.ttf"), 14)

        i = titleFont.render("PyWeek", 1, (128,128,128))
        surface.blit(i, (sw/2+sw-i.get_size()[0]/2+1, sh+6))

        i = titleFont.render("PyWeek", 1, self.foreground)
        surface.blit(i, (sw/2+sw-i.get_size()[0]/2, sh+5))

        headFont = pygame.font.Font(res.fontPath("volter.ttf"), 7)

        i = headFont.render("Inventory", 1, self.foreground, self.background)
        surface.blit(i, (sw+ 10, sh+30))


    def draw(self, surface):
        dirty = []

        if self.area.flash:
            x1, y1, z1 = self.area.flash
            x2, y2, z2 = hero_body.bbox.center
            self.area.flash = False
            d = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
            if d < 600:
                self.blank = True
                surface.fill((255,randint(0,255),255))
                dirty = [ surface.get_rect() ]


        elif self.blank:
            self.blank = False
            sw, sh = surface.get_size()
            surface.fill(self.background)
            mw = sw
            mh = sh * .75
            if not self.camera:
                self.camera = LevelCamera(self.area,((4,4), (mw, mh)),
                                          tmxdata=self.area.tmxdata)
            self.mapBorder = pygame.Rect((0,0,mw,mh+6))
            self.msgBorder = pygame.Rect((0,mh,sw,sh-mh))
            dirty = [((0,0), (sw, sh))]
            self.updateText = True


        else:
            if self.updateText:
                self.updateText = False
                surface.fill(self.background, self.msgBorder)
                self.border.draw(surface, self.msgBorder)
                log = "\n".join(self.area.messages[-5:])
                rect = self.msgBorder.inflate(-16,-12).move(0,1)
                gui.drawText(surface, log, (128,128,128), rect.move(1,1), self.msgFont)
                gui.drawText(surface, log, (0,0,0), rect, self.msgFont)
                dirty.append(self.msgBorder)

            self.camera.center(self.area.getPosition(self.hero))
            dirty.extend(self.camera.draw(surface))
            self.border.draw(surface, self.mapBorder)

        return dirty


    def addText(self, text):
        self.messages.append(text)
        self.updateText = True

    def update(self, time):
        if self.blank: return

        self.area.update(time)
        self.camera.update(time)

        body = self.area.getBody(self.hero)

        # don't move around if not needed
        if (not self.player_vector == self.old_player_vector) or \
           (not body.isFalling == self.old_falling):
            x, y, z = self.player_vector

            # allows you to move in air
            if body.isFalling:
                self.area.setForce(body, (x/3,y/3,body.acc.y))
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
        x = 0; y = 0; z = 0

        playing = self.hero.avatar.curAnimation.name

        for cls, cmd, arg in cmdlist:
            if arg == BUTTONUP:
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
                    if not self.elevatorDown():
                        if self.area.grounded(self.area.getBody(self.hero)):
                            if playing == "stand":
                                self.hero.avatar.play("crouch", loop_frame=4)

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
                    self.hero.use()


        self.player_vector = x, y*self.hero.move_speed, z


    def findLift(self, offset):
        body = self.area.getBody(self.hero)
        liftbbox = body.bbox.move(0,0,offset)
        shaftRect = self.area.toRect(body.bbox.move(0,0,-body.bbox.height/2))

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
            lift.parent.cancelCall()
            body = self.area.getBody(self.hero)
            self.area.movePosition(body, (0,0,-2), push=False)
            self.area.movePosition(lift, (0,0,-2), push=True, clip=False)
            lift.parent.animate()
            return True


    def elevatorDown(self):
        lift = self.findLift(1)

        if lift:
            lift.parent.cancelCall()
            body = self.area.getBody(self.hero)
            self.area.movePosition(lift, (0,0,2), push=True, clip=False)
            self.area.movePosition(body, (0,0,2), push=False)
            lift.parent.animate()
            return True


@receiver(emitText)
def displayText(sender, **kwargs):
    x1, y1, z1 = kwargs['position']
    x2, y2, z2 = hero_body.bbox.origin
    d = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
    state.updateText = True


@receiver(emitSound)
def playSound(sender, **kwargs):
    x1, y1, z1 = kwargs['position']
    x2, y2, z2 = hero_body.bbox.origin
    d = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
    try:
        vol = 1/d * 20 
    except ZeroDivisionError:
        vol = 1.0
    SoundMan.play(kwargs['filename'], volume=vol)


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


