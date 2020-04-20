#!/usr/bin/env python3

# Python monitoring code
# USAGE:  python3 app.py
#
# Last update: April 7, 2020

from time import time
from flask import Flask, render_template, make_response, jsonify, Response, request
import sqlite3
#import json
from flask import json
import chardet
from hevclient import HEVClient
from commsConstants import DataFormat


WEBAPP = Flask(__name__)

# Instantiating the client
hevclient = HEVClient()


def getList(dict):
    return [*dict]

@WEBAPP.route('/', methods=['GET', 'POST'])
def hello_world():
   return render_template('index.html', result=live_data())


@WEBAPP.route('/settings')
def settings():
    return render_template('settings.html', result=live_data())

@WEBAPP.route('/charts')
def charts():
    return render_template('charts.html', result=last_N_data())

@WEBAPP.route('/charts2')
def charts2():
    return render_template('charts2.html')

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
    Send configuration data to the Arduino
    """
    output = []
    var_1 = request.form['pressure_air_supply']
    var_2 = request.form['variable2']
    var_3 = request.form['variable3']
    var_4 = request.form['variable4']
    var_5 = request.form['variable5']
    var_6 = request.form['variable6']
  
    patient_name = request.form['patient_name']

 
    multiple_appends(output, var_1, var_2, var_3, var_4, var_5, var_6)
    
    converted_output = [float(i) for i in output] 

    hevclient.set_thresholds(converted_output)

    return render_template('index.html', result=live_data(), patient=patient_name)




@WEBAPP.route('/live-data', methods=['GET'])
def live_data():
    """
    Query the sqlite3 table for variables
    Output in json format
    """

    list_variables = []
    list_variables.append("created_at")
    list_variables.extend(getList(DataFormat().getDict()))

    data = {key: None for key in list_variables}

    united_var = ','.join(list_variables)

    sqlite_file = 'database/HEC_monitoringDB.sqlite'
    with sqlite3.connect(sqlite_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT {var} "
        "FROM hec_monitor ORDER BY ROWID DESC LIMIT 1".format(var=united_var))
        
        fetched = cursor.fetchone()

        for index, item in enumerate(list_variables):
            if item == 'created_at':
                data[item] = fetched[index]
            else:
                data[item] = round(fetched[index],2)   


    response = make_response(json.dumps(data).encode('utf-8') )
    response.content_type = 'application/json'

    
    #return Response(json.dumps(data),  mimetype='application/json')
    return response

@WEBAPP.route('/last_N_data', methods=['GET'])
def last_N_data():
    """
    Query the sqlite3 table for variables
    Output in json format
    """
    N = 30
    list_variables = []
    list_variables.append("created_at")
    list_variables.extend(getList(dataFormat().getDict()))


    united_var = ','.join(list_variables)

    sqlite_file = 'database/HEC_monitoringDB.sqlite'
    fetched_all = []

    with sqlite3.connect(sqlite_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT {var} "
        "FROM hec_monitor ORDER BY ROWID DESC LIMIT {entries}".format(var=united_var, entries=N))
        
        fetched = cursor.fetchall()
        for el in fetched:
          data = {key: None for key in list_variables}

          for index, item in enumerate(list_variables):
              if item == 'created_at':
                  data[item] = el[index]
              else:
                  data[item] = round(el[index],2)   
          fetched_all.append(data)
          #print(fetched_all)

    response = make_response(json.dumps(fetched_all).encode('utf-8') )
    response.content_type = 'application/json'

    return response


@WEBAPP.route('/live-alarms', methods=['GET'])
def live_alarms():
    """
    Query the sqlite3 table for alarms
    Output in json format
    """

    data = {'created_at' : None, 'alarms' : None}

    sqlite_file = 'database/HEC_monitoringDB.sqlite'
    with sqlite3.connect(sqlite_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT created_at, alarms "
        "FROM hec_monitor ORDER BY ROWID DESC LIMIT 1")

        fetched = cursor.fetchone()

        data['created_at'] = fetched[0]
        data['alarms'] = fetched[1]

    response = make_response(json.dumps(data).encode('utf-8') )
    response.content_type = 'application/json'

    return response


@WEBAPP.route('/last_N_alarms', methods=['GET'])
def last_N_alarms():
    """
    Query the sqlite3 table for the last N alarms
    Output in json format
    """
    N = 10
    data = {'created_at' : None, 'alarms' : None}

    sqlite_file = 'database/HEC_monitoringDB.sqlite'
    with sqlite3.connect(sqlite_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT created_at, alarms "
        "FROM hec_monitor ORDER BY ROWID DESC LIMIT {}".format(N))

        fetched = cursor.fetchall()

    response = make_response(json.dumps(fetched).encode('utf-8') )
    response.content_type = 'application/json'

    return response


if __name__ == '__main__':
    WEBAPP.run(debug=True, host='127.0.0.1', port=5000)






