#!/usr/bin/env python3
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



# Python monitoring code
# USAGE:  python3 app.py
#
# Last update: May 5, 2020

import time
import sqlite3
import argparse
from hevclient import HEVClient
from CommsCommon import DataFormat, CycleFormat, ReadbackFormat, AlarmFormat, TargetFormat, BatteryFormat, PersonalFormat, LogMsgFormat
from datetime import datetime
import logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

import io
import csv
import sys
import argparse
import sqlite3
from datetime import datetime
import threading

#SQLITE_FILE = 'database/HEV_monitoringDB.sqlite'  # name of the sqlite database file
#SQLITE_FILE = 'hev::memory:?cache=shared'
#SQLITE_FILE = 'file:hev?mode=memory&cache=shared'
SQLITE_FILE = '/dev/shm/HEV_monitoringDB.sqlite'  # use the linux shared memory pool as a file system
MASTER_TABLE_NAME = 'hev_monitor' # this table keeps track of the data we get through keys to other tables
DATA_TABLE_NAME = 'hev_monitor_data'  # name of the table to be created for payload type data
CYCLE_TABLE_NAME = 'hev_monitor_cycle'  # name of the table to be created for payload type cycle
TARGET_TABLE_NAME = 'hev_monitor_target'  # name of the table to be created for payload type target
READBACK_TABLE_NAME = 'hev_monitor_readback'  # name of the table to be created for payload type readback
ALARM_TABLE_NAME = 'hev_monitor_alarm'  # name of the table to be created for payload type readback
PERSONAL_TABLE_NAME = 'hev_personal_target'  # name of the table to be created for payload type personal
LOGMSG_TABLE_NAME = 'hev_monitor_logmsg'  # name of the table to be created for payload type personal


def getList(dict):
    return [*dict]


payload_types = {
    #'DATA' : {'table_name' : DATA_TABLE_NAME, 'format' : DataFormat().getDict(), 'id' : 'DataID'},
    'LOGMSG' : { 'table_name' : LOGMSG_TABLE_NAME, 'format' : LogMsgFormat().getDict(), 'id' : 'LogMsgID' },
    #'PERSONAL' : { 'table_name' : PERSONAL_TABLE_NAME, 'format' : PersonalFormat().getDict(), 'id' : 'PersonalID' },
}


class LogClient(HEVClient):
    def __init__(self):
        self.timestr = time.strftime("%Y%m%d-%H%M%S")
        super().__init__(polling=True)

    def start_client(self):
        """runs in other thread - works as long as super goes last and nothing
        else is blocking. If something more than a one-shot process is needed
        then use async"""
        # call for all the targets and personal details
        # when starting the web app so we always have some in the db
        super().start_client()


    def get_updates(self, payload):
        """callback from the polling function, payload is data from socket"""
        self.monitoring(payload)


    def monitoring(self, payload):
        epoch = datetime(1970, 1, 1)
        current_time = datetime.now()

        # Computing the time in seconds since the epoch because easier to manipulate.
        timestamp = (current_time -epoch).total_seconds() * 1000


        try:
            if payload != None and payload['type'] == "LOGMSG" :
                add_to_existing = False
                payload_type = payload['type']
                data_packet = { el : payload[payload_type][el] for el in payload_types[payload_type]['format']}
                row = [payload_type]+[val for val in payload[payload_type].values()]
                print(row[4])
        except KeyboardInterrupt:
            sys.exit(0)


# Instantiating the client
client = LogClient()



if __name__ == '__main__':
  try:
    client.start_client()
  except KeyboardInterrupt:
    sys.exit(0)
    
