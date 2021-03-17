#!/usr/bin/env python3
#
# Copyright (C) 2021 Fabien Bonneval <fabien.bonneval@enac.fr>
#
# This file is part of paparazzi.
#
# paparazzi is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# paparazzi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paparazzi; see the file COPYING.  If not, see
# <http://www.gnu.org/licenses/>.
#

from lxml import etree
#from typing import List
import sys
from os import path, getenv
import time
from xml_utils import get_attrib, get_attrib_default

PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../')))
sys.path.append(PPRZ_HOME + "/var/lib/python")
#from pprzlink.ivy import IvyMessagesInterface
#from pprzlink.message import PprzMessage

class Airframe:
    def __init__(self, airframe_xml_path):
        self.name = ""
        pass

    @staticmethod
    def parse(airframe_xml_path):
        airframe_tree = etree.parse(airframe_xml_path)
        root = airframe_tree.getroot()
        name = root.attrib["name"]
        print(name)

if __name__ == "__main__":
    Airframe.parse("{}/conf/airframes/ENAC/fixed-wing/tawaki.xml".format(PPRZ_HOME))

