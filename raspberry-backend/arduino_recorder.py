#!/usr/bin/env python3

# HEV monitoring application
# USAGE:  python3 arduino_recorder.py
#
# Last update: April 4, 2020

import sys
import time
import argparse
import sqlite3
from datetime import datetime
import threading
from hevclient import HEVClient
from commsConstants import DataFormat

SQLITE_FILE = 'database/HEC_monitoringDB.sqlite'  # name of the sqlite database file
TABLE_NAME = 'hec_monitor'  # name of the table to be created

def getList(dict): 
    return [*dict] 

# List of data variables in the data packet from the Arduino
data_format = getList(DataFormat().getDict())


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
   
        exec_string = "created_at  INTEGER  NOT NULL, "
        for var in data_format:
           exec_string += var + "  FLOAT  NOT NULL, "
        exec_string += "alarms  STRING  NOT NULL "

        # Setting the maximum size of the DB to 100 MB
        conn.execute("PRAGMA max_page_count = 204800")
        conn.execute("PRAGMA page_size = 512")

        conn.execute('''CREATE TABLE IF NOT EXISTS {tn} ({ex_str});'''
           .format(tn=TABLE_NAME, ex_str=exec_string))

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
                
                data_packet = { el : data_receiver[el] for el in data_format}
                data_packet.update({"time" : timestamp})
                data_packet.update({"alarms" : data_alarms})

                print("Writing to database ...")
                try:
                    exec_string = "( :time, "
                    for el in data_format: 
                         exec_string += ":" + el + ", "
                    exec_string += ":alarms) "

                    cursor.execute(
                            'INSERT INTO {tn} VALUES {ex_str} '
                            .format(tn=TABLE_NAME, ex_str=exec_string), data_packet
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
