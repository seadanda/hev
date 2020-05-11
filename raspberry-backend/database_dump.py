#!/usr/bin/env python3

# HEV database dump for debugging
# USAGE:  python3 database_dump.py --backup_db=True --start_date=20200408-1834
#
# Dumps the data from the backup or main db for debugging purposes.
#

import sys
import time
import argparse
import sqlite3
from datetime import datetime, timedelta
import threading

#SQLITE_FILE = 'database/HEC_monitoringDB.sqlite'  # name of the sqlite database file
SQLITE_BACKUPFILE = 'database/HEV_monitoringDB.sqlite'  # name of the sqlite backup database file
TABLE_NAME = 'hev_monitor'  # name of the table to be created

def load_data(sqFile, startTime):
    """
    Load the database table and select data between a time+date and the end of the file
    """
    try:
        conn = sqlite3.connect(sqFile)
    except sqlite3.Error as err:
        raise Exception("sqlite3 Error. Load {} failed: {}".format(sqFile,str(err)))
    finally:
        print("Loaded {} ".format(sqFile))
    #
    # load data
    #
    cursor = conn.cursor()
    try:
        cursor.execute('PRAGMA table_info({tablename})'.format(tablename=TABLE_NAME))
        tableInfo = cursor.fetchall()
        # Computing the time in seconds since the epoch because easier to manipulate.
        epoch = datetime(1970, 1, 1, 0, 0)
        startFromEpoch = (startTime - epoch).total_seconds() * 1000
        cursor.execute('SELECT * FROM {tablename} WHERE created_at > {startFromEpoch};'.\
                       format(tablename=TABLE_NAME, startFromEpoch=startFromEpoch))
        rows = cursor.fetchall()
    except sqlite3.Error as err:
        raise Exception("sqlite3 Error. Reading {} failed: {}".format(sqFile,str(err)))
    return {'tableInfo':tableInfo, 'rows':rows}

def printRows(dataTable):
    """
    Format a row to the screen
    """
    #
    # format print string
    #
    tableInfo = dataTable['tableInfo']
    rows = dataTable['rows']
    fmt=" ".join(["{yyyy:4d}-{mm:02d}-{dd:02d} {HH:02d}:{MM:02d}", # date of datetaken
                  ]) #pressure
    fmtOther = []
    # others added later
    for col in tableInfo[4:]:
        if( col[2] == "FLOAT" ):
            fmtOther.append(" {:8.2f}")
        if( col[2] == "INTEGER" ):
            fmtOther.append(" {:8i}")
    fmt += " {other} : {alarm}"
    epoch = datetime(1970, 1, 1, 0, 0)
    #
    # header
    #
    #header = "#  Date    Time   Temp.  Pres. "
    header = "#  "
    for col in tableInfo[0:]:
        print(col)
        colNameFull = col[1]
        colNameShort = col[1]
        if(len(colNameFull)>8):
            underScorePos = [] # count underscores
            for p in range(len(colNameFull)):
                if colNameFull[p] == '_' :
                    underScorePos.append(p)
            if( len(underScorePos) == 0 ):
                colNameShort = colNameFull[:8] # first 8 chars only
            elif(len(underScorePos) == 1 ):
                p = underScorePos[0]
                colNameShort = colNameFull[:4] + colNameFull[p+1].upper()+colNameFull[p+2:p+5] # Two groups of 4
            else:
                colNameShort = colNameFull[:2] # first two char + 2 after each _
                for p in underScorePos[:3]: # first three only if more
                    colNameShort += colNameFull[p+1].upper()+colNameFull[p+2]
        header += "  {:>8s}".format(colNameShort)
    #header += " : Alarm state"
    #
    # Loop over rows passed and print
    #
    nPrint = 0
    for r in rows:
        if( nPrint%50 == 0 ): print("\n", header, "\n") # header every 50 rows
        nPrint += 1
        otherTxt = ""
        for el in range(len(r)):
            if isinstance(r[el], float) or isinstance(r[el], int):
                otherTxt += f'{r[el]:8.2f}' 
            else: # isinstance(r[el], str):
                otherTxt += f'  { r[el] }'


                
            #otherTxt += f'{i:8.2f}' if isinstance(i, float) or isinstance(i, int) else f'  {i}  '
            #print(r[i])
            #otherTxt += fmtOther[i].format(r[4+i])
        #print(otherTxt)
        rowDateTime = (epoch + timedelta(seconds=r[0]/1000))
        print(fmt.format(yyyy=rowDateTime.year,
                         mm=rowDateTime.month,
                         dd=rowDateTime.day,
                         HH=rowDateTime.hour,
                         MM=rowDateTime.minute,
                         other=otherTxt,
                         alarm=r[0]))
                         


def parse_args():
    global SQLITE_BACKUPFILE
    parser = argparse.ArgumentParser(description='Python script for checking monitoring database')
    parser.add_argument("-db", "--database", type=str, default=SQLITE_BACKUPFILE,
                        help=f"Database to check, it missing assumes backup db {SQLITE_BACKUPFILE}")
    parser.add_argument("-s", "--start_date", dest="start_date",
                        default=datetime.today() - timedelta(days = 1, seconds=0),
                        type=lambda d: datetime.strptime(d, '%Y%m%d-%H%M'),
                        help="Date in the format yyyymmdd-HHMM (for example 20200409-14:30)")
    return parser.parse_args()

if __name__ == "__main__":
    ARGS = parse_args()
    dataTable = load_data(ARGS.database, ARGS.start_date)
    print("dataTable Info =")
    print("\n".join("  {} \t: {}".format(t[1],t[2]) for t in dataTable['tableInfo']))
    print("Num rows = ",len(dataTable['rows']))
    printRows(dataTable)
