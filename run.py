from lib2d.game import Game
from lib2d.statedriver import driver as sd
from lib2d import gfx, res
import pygame, os



class TestGame(Game):
    def start(self):
        from lib2d.objects import loadObject
        from lib.levelstate import LevelState
        
        #gfx.set_screen((640, 480), 2, "scale")
        gfx.set_screen((640, 480))
        self.sd.reload_screen()
        path = os.path.join("resources", "worlds", "world")
        world = loadObject(path)
        area = world.getChildByGUID(1001)
        self.sd.start(LevelState(area))
        self.sd.run()


if __name__ == "__main__":
    TestGame().start()
