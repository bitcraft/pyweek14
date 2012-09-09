"""planes Setup Script

   Copyright 2010-2012 Florian Berger <fberger@florian-berger.de>
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

# work started on 10. December 2010

import distutils.core
import glob
import os.path
import planes

# TODO: add resources directory

distutils.core.setup(name = "planes",
                     version = planes.VERSION,
                     author = "Florian Berger",
                     author_email = "fberger@florian-berger.de",
                     url = "http://florian-berger.de/software/planes/",
                     description = "planes - A Hierarchical Surface Framework for Pygame",
                     license = "GPL",
                     packages = ["planes",
                                 "planes.gui"],
                     requires = ["pygame (>=1.9.1)"],
                     provides = ["planes",
                                 "planes.gui"],
                     scripts = ["examples/planes_interactive.py"],
                     package_data = {"planes" : ["Vera.ttf", "VeraBd.ttf"]},
                     data_files = [("share/doc/planes-{0}".format(planes.VERSION),
                                    glob.glob(os.path.join("doc", "*.*")) + ["NEWS"])])
