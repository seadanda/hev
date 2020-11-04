# © Copyright CERN, Riga Technical University and University of Liverpool 2020.
# All rights not expressly granted are reserved. 
# 
# This file is part of hev-sw.
# 
# hev-sw is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public Licence as published by the Free
# Software Foundation, either version 3 of the Licence, or (at your option)
# any later version.
# 
# hev-sw is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
# for more details.
# 
# You should have received a copy of the GNU General Public License along
# with hev-sw. If not, see <http://www.gnu.org/licenses/>.
# 
# The authors would like to acknowledge the much appreciated support
# of all those involved with the High Energy Ventilator project
# (https://hev.web.cern.ch/).


import json

class gpio:
    DUMMY = True
    IN = 0
    OUT = 0
    SPI = 0
    I2C = 0
    HARD_PWM = 0
    SERIAL = 0
    UNKNOWN = 0

    PUD_DOWN = 0

    BCM = 0

    @staticmethod
    def setmode(mode):
        pass

    @staticmethod
    def setup(pin, mode, pull_up_down):
        pass

    def __init__(self):
        self._dumpfile = "share/battdump.dict"
        self._iter = self.generator()
        self._fileline = self.update()
        self._pins = {5: "bat",
                      6: "ok",
                      12: "alarm",
                      13: "rdy2buf",
                      19: "bat85",
                      7: "prob_elec"}

    def update(self):
        return json.loads(next(self._iter).replace("'",'"').replace("True","true").replace("False","false"))

    def generator(self):
        while True:
            with open(self._dumpfile, 'r') as f:
                try:
                    for line in f:
                        yield line
                except StopIteration:
                    pass

    def input(self, pin):
        currline = self._fileline
        if pin == 7:
            # get next line from file
            self._fileline = self.update()
        return currline[self._pins[pin]]
