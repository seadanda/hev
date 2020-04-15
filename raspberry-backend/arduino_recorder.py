#!/usr/bin/env python3

# HEV monitoring application
# USAGE:  python3 arduino_recorder.py
#
# Last update: April 4, 2020

import sys
import time
import argparse
import sqlite3
from random import random
from datetime import datetime
import threading
from hevclient import HEVClient


SQLITE_FILE = 'database/HEC_monitoringDB.sqlite'  # name of the sqlite database file
TABLE_NAME = 'hec_monitor'  # name of the table to be created

def get_temperature():
    """
    Returns a random number to simulate data obtained from a sensor
    """
    return random() * 20


def database_setup():
    '''
    This function creates the sqlite3 table with the timestamp column 
    and the columns for the arduino packet data  
    '''
    print('Creating ' + TABLE_NAME + ' table..' )

    # Create the table if it does not exist
    try:
        # Connecting to the database file
        conn = sqlite3.connect(SQLITE_FILE)
        conn.execute('''CREATE TABLE IF NOT EXISTS ''' + TABLE_NAME + ''' (
           created_at     INTEGER        NOT NULL,
           alarms         STRING         NOT NULL,
           version       FLOAT           NOT NULL,           
           fsm_state    FLOAT           NOT NULL,
           pressure_air_supply    FLOAT           NOT NULL,
           pressure_air_regulated    FLOAT           NOT NULL,
           pressure_o2_supply    FLOAT           NOT NULL,   
           pressure_o2_regulated    FLOAT           NOT NULL,
           pressure_buffer    FLOAT           NOT NULL,
           pressure_inhale    FLOAT           NOT NULL,
           pressure_patient    FLOAT           NOT NULL,
           temperature_buffer    FLOAT           NOT NULL,
           pressure_diff_patient    FLOAT           NOT NULL,
           readback_valve_air_in    FLOAT           NOT NULL,
           readback_valve_o2_in    FLOAT           NOT NULL,
           readback_valve_inhale    FLOAT           NOT NULL,
           readback_valve_exhale    FLOAT           NOT NULL,
           readback_valve_purge    FLOAT           NOT NULL,
           readback_mode    FLOAT           NOT NULL                
           );'''
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as err:
        raise Exception("sqlite3 Error. Create failed: {}".format(str(err)))
    finally:
        print('Table ' + TABLE_NAME + ' created successfully!')

def monitoring(source_address):
    '''
    Store arduino data in the sqlite3 table. 
    '''

    # Instantiating the client
    hevclient = HEVClient()
    print(hevclient.send_cmd("CMD_START"))

    epoch = datetime(1970, 1, 1)

    with sqlite3.connect(SQLITE_FILE) as conn:
        cursor = conn.cursor()
        while True:
            current_time = datetime.now()

            # Computing the time in seconds since the epoch because easier to manipulate. 
            timestamp = (current_time -epoch).total_seconds() * 1000
  
            data_receiver = hevclient.get_values()
            data_alarms = hevclient.get_alarms()
            
            if data_receiver != None:

                # data alarms can have length of 6, joining all the strings
                if data_alarms != None:
                    data_alarms = ','.join(data_alarms)
                else:
                    data_alarms = "none"


                data_packet = {
                    'time' : timestamp,
                    'alarms' : data_alarms,
                    'version': data_receiver["version"],
                    'fsm_state': data_receiver["fsm_state"],
                    'pressure_air_supply': data_receiver["pressure_air_supply"],
                    'pressure_air_regulated': data_receiver["pressure_air_regulated"],
                    'pressure_o2_supply': data_receiver["pressure_o2_supply"], 
                    'pressure_o2_regulated': data_receiver["pressure_o2_regulated"], 
                    'pressure_buffer': data_receiver["pressure_buffer"], 
                    'pressure_inhale': data_receiver["pressure_inhale"], 
                    'pressure_patient': data_receiver["pressure_patient"], 
                    'temperature_buffer': data_receiver["temperature_buffer"], 
                    'pressure_diff_patient': data_receiver["pressure_diff_patient"], 
                    'readback_valve_air_in': data_receiver["readback_valve_air_in"], 
                    'readback_valve_o2_in': data_receiver["readback_valve_o2_in"], 
                    'readback_valve_inhale': data_receiver["readback_valve_inhale"], 
                    'readback_valve_exhale': data_receiver["readback_valve_exhale"], 
                    'readback_valve_purge': data_receiver["readback_valve_purge"], 
                    'readback_mode': data_receiver["readback_mode"]
                }

                print("Writing to database ...")
                try:
                    cursor.execute(
                            'INSERT INTO {tn} VALUES '
                            '(:time, :alarms,  :version, '
                            ':fsm_state, :pressure_air_supply, '
                            ':pressure_air_regulated, :pressure_o2_supply,'
                            ':pressure_o2_regulated, :pressure_buffer,'
                            ':pressure_inhale, :pressure_patient,'
                            ':temperature_buffer, :pressure_diff_patient,'
                            ':readback_valve_air_in, :readback_valve_o2_in,'
                            ':readback_valve_inhale, :readback_valve_exhale,'
                            ':readback_valve_purge, :readback_mode)'
                            .format(tn=TABLE_NAME), data_packet
                    )
                    conn.commit()
                except sqlite3.Error as err:
                     raise Exception("sqlite3 error. Insert into database failed: {}".format(str(err)))
                finally:                  
                    sys.stdout.flush()
                    time.sleep(1)

def progress(status, remaining, total):
    print(f'Copied {total-remaining} of {total} pages...')


def db_backup(backup_time):
    threading.Timer(backup_time, db_backup, [backup_time]).start()
    print("Executing DB backup")
    try:
        # Existing DB
        sqliteCon = sqlite3.connect(SQLITE_FILE)
        # Backup DB
        backupCon = sqlite3.connect("database/HEC_monitoringDB_backup.sqlite")    
        with backupCon:
            sqliteCon.backup(backupCon, pages=5, progress=progress)
        print("Backup successful")
    except sqlite3.Error as err:
        raise Exception("sqlite3 error. Error during backup: {}".format(str(err)))
    finally: 
        if(backupCon):
            backupCon.close()
            sqliteCon.close()
    

def parse_args():
    parser = argparse.ArgumentParser(description='Python script monitorign Arduino data')
    parser.add_argument('--source', default='ttys0 or similar')
    parser.add_argument('--backup_time', type=int, default=600)
    return parser.parse_args()

if __name__ == "__main__":
    ARGS = parse_args()
    database_setup()
    db_backup(ARGS.backup_time)
    monitoring(ARGS.source)
