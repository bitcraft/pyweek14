#!/usr/bin/python3

"""Run an interactive planes-Session.

   Start this script with 'python -i' or import it as a module

   Copyright 2010 Florian Berger <fberger@florian-berger.de>
"""

# This file is part of planes.
#
# planes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# planes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with planes.  If not, see <http://www.gnu.org/licenses/>.

# work started on 04. November 2010

import sys
import readline
import traceback

# Add current and parent directory. One of them is supposed to contain the
# planes package.
#
sys.path.append("../")
sys.path.append("./")

import pygame
import planes
import planes.gui
import threading
import code

print("creating window")

window = planes.Display((400, 300))
window.grab_dropped_planes = True
window.image.fill((127, 127, 127))
pygame.display.set_caption("planes Interactive Live Test")

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
white = (255, 255, 255)

def click(*args):
    print("Click! args: {0}".format(args))

plane = planes.Plane("plane",
                         pygame.Rect((200, 50), (100, 100)),
                         draggable = True)

plane.image.fill(yellow)

button = planes.gui.Button("Button",
                               pygame.Rect((50, 50), (100, 50)),
                               click)

container = planes.gui.Container("container", padding = 10)
container.rect.topleft = (250, 50)

textbox = planes.gui.TextBox("textbox", pygame.Rect((10, 10), (200, 30)))
window.key_sensitive(textbox)

clock = pygame.time.Clock()
fps = clock.get_fps

helptext = """---------------------------------------------------------------------------
You can now interact with planes.

window                            - Root window, instance of planes.Display
plane, button, textbox, container - Test instances, try window.sub(plane)
red, green, blue, yellow, white   - Color tuples for your convenience
fps()                             - print current framerate
click()                           - A convenience callback function

Plane(name, rect, drag=False, grab=False)

Plane.image               - The pygame.Surface for a Plane
Plane.rect                - The render position on the parent plane
Plane.subplanes           - Dict of subplanes
Plane.draggable           - Flags for Plane configuration
Plane.grab_dropped_planes - Flags for Plane configuration

Plane.sub(Plane)          - Add plane as a subplane of this Plane.

print(helptext)           - Print this help text

Close the Pygame window and 'raise SystemExit' or press [Ctrl]+[D] to exit.
---------------------------------------------------------------------------
"""

def mainloop(framerate):
    """Runs a pygame / planes main loop.
       framerate is the framerate.
       This must be run in the main thread, otherwise pygame.event will not
       receive any events under MS Windows.
    """

    print("about to start main loop")

    while True:
        events = pygame.event.get()

        for event in events:

            if event.type == pygame.QUIT:
                print("got pygame.QUIT, terminating in mainloop()")
                pygame.quit()
                raise SystemExit

        window.process(events)
        window.update()
        window.render()

        pygame.display.flip()

        # Slow down to framerate given
        #
        clock.tick(framerate)

def run_interactive_console(locals_dict):

    ic = code.InteractiveConsole(locals_dict)

    ic.interact(helptext)

if __name__ == "__main__":

    interactive_console_thread = threading.Thread(target = run_interactive_console,
                                                  name = "interactive_console",
                                                  args = (locals(),))

    print("starting interactive console thread")

    interactive_console_thread.start()

    print("starting main loop in main thread")

    try:
        mainloop(60)

    except:
        print("Exception in mainloop():")
        print(traceback.format_exc())
        pygame.quit()
        raise SystemExit
