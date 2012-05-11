from lib.levelstate import LevelState
from lib import world

from lib2d.gamestate import GameState
from lib2d.cmenu import cMenu
from lib2d.statedriver import driver as sd
from lib2d.objects import loadObject
from lib2d import res, gui

import pygame, os


class TitleScreen(GameState):

    def activate(self):
        self.background = (109, 109, 109)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
        self.counter = 0
        self.game = None
        self.activated = True
        self.reactivate()


    def reactivate(self):
        if self.game:
            self.menu = cMenu(((32,20), sd.get_size()),
                20, -5, 'vertical', 100,
                [('New Game', self.new_game),
                ('Continue', self.continue_game),
                ('Introduction', self.show_intro),
                ('Save and Quit', self.savequit_game),
                ('Quit', self.quit_game)],
                font="visitor1.ttf", font_size=20)
        else:
            self.menu = cMenu(((32,20), sd.get_size()),
                20, -5, 'vertical', 100,
                [('New Game', self.new_game),
                ('Continue', self.continue_game),
                ('Introduction', self.show_intro),
                ('Quit', self.quit_game)],
                font="visitor1.ttf", font_size=20)

        self.menu.ready()
        self.redraw = True


    def handle_event(self, event):
        self.menu.handle_event(event)


    def draw(self, surface):
        if self.redraw:
            self.redraw = False
            if self.game:
                self.border.draw(surface, ((0,0), surface.get_size()))
            else:
                self.borderFilled.draw(surface, ((0,0), surface.get_size()))

        self.menu.draw(surface)


    def new_game(self):
        self.game = world.build()
        level = self.game.getChildByGUID(5001)
        sd.start(LevelState(level))


    def continue_game(self):
        if self.game == None:
            try:
                path = os.path.join("resources", "save", "save")
                self.game = loadObject(path)
            except IOError:
                return self.new_game()

        level = self.game.getChildByGUID(5001)
        sd.start(LevelState(level))


    def show_intro(self):
        s = Cutscene(res.miscPath("intro.txt", "scripts")) 
        sd.start_restart(s)


    def savequit_game(self):
        if self.game:
            path = os.path.join("resources", "saves", "save")
            [ i.unload() for i in self.game.getChildren() ]
            self.game.save(path)
        self.quit_game()


    def quit_game(self):
        sd.done() 

