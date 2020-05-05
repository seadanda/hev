#!/usr/bin/env python3

# Python monitoring code
# USAGE:  python3 app.py
#
# Last update: May 5, 2020

from time import time
from flask import Flask, render_template, make_response, jsonify, Response, request
import sqlite3
import argparse
from flask import json
import chardet
from hevclient import HEVClient
from CommsCommon import DataFormat
from datetime import datetime

WEBAPP = Flask(__name__)

# Instantiating the client
hevclient = HEVClient()

sqlite_file = 'database/HEV_monitoringDB.sqlite'
TABLE_NAME = 'hev_monitor'  # name of the table to be created
N = 300 # number of entries to request for alarms and data (300 = 60 s of data divided by 0.2 s interval)


def getList(dict):
    return [*dict]

@WEBAPP.route('/', methods=['GET', 'POST'])
def hello_world():
   return render_template('index.html', result=live_data())

@WEBAPP.route('/testing', methods=['GET', 'POST'])
def prototype():
   return render_template('index_prototype.html', result=live_data())

@WEBAPP.route('/settings')
def settings():
    return render_template('settings.html', result=live_data())

@WEBAPP.route('/charts')
def charts():
    return render_template('charts.html', result=last_N_data())

@WEBAPP.route('/charts2')
def charts2():
    return render_template('charts2.html')

@WEBAPP.route('/chartsLoop')
def chartsLoop():
    return render_template('chartsLoop.html')

@WEBAPP.route('/logs')
def logs():
    return render_template('logs.html', result=last_N_alarms())    

@WEBAPP.route('/fan')
def fan():
    return render_template('fan.html', result=live_data())


def multiple_appends(listname, *element):
    listname.extend(element)

@WEBAPP.route('/send_cmd', methods=['POST'])
def send_cmd():
    """
    Send command to the data server
    """ 
    web_form = request.form
    if web_form.get('start') == "START":
        print(hevclient.send_cmd("GENERAL", "START"))
    elif web_form.get('stop') == "STOP":
        print(hevclient.send_cmd("GENERAL", "STOP"))
    elif web_form.get('reset') == "RESET":
        print(hevclient.send_cmd("GENERAL", "RESET"))
    #return render_template('index.html', result=live_data())
    return ('', 204)
    

@WEBAPP.route('/data_handler', methods=['POST'])
def data_handler():
    """
    Send timeout thresholds to the Arduino
    """
    #data = {}    # empty dict to store data
    #data['variable'] = request.get_json(force=True)
    data = request.get_json(force=True)
    

    print(data['name'])
    print(data['value'])

    print(hevclient.send_cmd("SET_TIMEOUT", "BUFF_FILL", int(data['value'])))

    return ('', 204)


def number_rows(table_name):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()    			
    #get the count of tables with the name
    c.execute(''' SELECT count(*) FROM {tn} '''.format(tn=table_name))  

    values = c.fetchone()
    print(values[0])

    #commit the changes to db			
    conn.commit()
    #close the connection
    conn.close()
    return values[0]


def check_table(table_name):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()    			
    #get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{tn}' '''.format(tn=table_name))  
    existence = False

    #if the count is 1, then table exists
    if c.fetchone()[0]==1 : 
        existence = True
        print('Table exists.')
    else :
    	print('Table does not exist.')
    			
    #commit the changes to db			
    conn.commit()
    #close the connection
    conn.close()
    return existence



@WEBAPP.route('/live-data', methods=['GET'])
def live_data():
    """
    Get live data from the hevserver
    Output in json format
    """
    response = make_response(json.dumps(hevclient.get_values()).encode('utf-8') )
    response.content_type = 'application/json'
    return response


@WEBAPP.route('/last_N_data', methods=['GET'])
def last_N_data():
    """
    Query the sqlite3 table for variables
    Output in json format
    """

    list_variables = []
    list_variables.append("created_at")
    list_variables.extend(getList(DataFormat().getDict()))

    united_var = ','.join(list_variables)

    fetched_all = []
    
    if check_table(TABLE_NAME) and number_rows(TABLE_NAME) > N:
        with sqlite3.connect(sqlite_file) as conn:
            cursor = conn.cursor()
            cursor.execute(" SELECT {var} "
            " FROM {tn} ORDER BY ROWID DESC LIMIT {size} ".format(tn=TABLE_NAME, var=united_var, size=N))
            
            fetched = cursor.fetchall()
            for el in fetched:
              data = {key: None for key in list_variables}
    
              for index, item in enumerate(list_variables):
                      data[item] = el[index]

              fetched_all.append(data)
    else:
        for i in range(N):
              data = {key: None for key in list_variables}
              for index, item in enumerate(list_variables):
                      data[item] = ""

              fetched_all.append(data)

    response = make_response(json.dumps(fetched_all).encode('utf-8') )
    response.content_type = 'application/json'

    return response


@WEBAPP.route('/live-alarms', methods=['GET'])
def live_alarms():
    """
    Get live alarms from the hevserver
    Output in json format
    """
    data = {'timestamp' : None, 'alarms' : None}
    data_alarms = hevclient.get_alarms()
    data_receiver = hevclient.get_values()


    if data_alarms != None:
        data_alarms = ','.join(data_alarms)
    else:
        data_alarms = "none"

    data["alarms"] = data_alarms

    if data_receiver is not None:
        data["timestamp"] = data_receiver['timestamp']/1000
    else:
        data["timestamp"] = "none"

    response = make_response(json.dumps(data).encode('utf-8') )
    response.content_type = 'application/json'
    return response


@WEBAPP.route('/last_N_alarms', methods=['GET'])
def last_N_alarms():
    """
    Query the sqlite3 table for the last N alarms
    Output in json format
    """
    data = {'timestamp' : None, 'alarms' : None}

    if check_table(TABLE_NAME):
        with sqlite3.connect(sqlite_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, alarms "
            "FROM {tn} ORDER BY ROWID DESC LIMIT {size}".format(tn=TABLE_NAME, size=N))
            fetched = cursor.fetchall()
    else:
        fetched = []
        for i in range(N):
              data['timestamp'] = "none"
              data['alarms'] = "none"
              fetched.append(data)


    response = make_response(json.dumps(fetched).encode('utf-8') )
    response.content_type = 'application/json'
    return response


def parse_args():
    parser = argparse.ArgumentParser(description='HEV webserver')
    parser.add_argument('--host', default='127.0.0.1')    
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = parse_args()

    WEBAPP.run(debug=True, host=ARGS.host, port=5000)







