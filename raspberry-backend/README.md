## High Energy Ventilator (HEV)

### Raspberry Pi backend and monitoring frontend for the High Energy Ventilators project 

- Author: Adam Abed Abud <
- Mail: adam.abed.abud@cern.ch
- Last update: April 2, 2020


**Backend:** Python3, Flask, sqlite3 
**Frontend:** Javascript, HTML, ChartsJS


# Usage
Before starting the web application you will need the following packages to be installed on the RP:

```sh
sudo pip3 install flask
sudo apt-get install sqlite3
```

Start the HEV server

```sh
cd raspberry-dataserver
python3 hevserver.py

# In case you want to test with random generated numbers
python3 hevserver.py --inputFile share/byteArray.dump
```


```sh
cd raspberry-backend
python3 arduino_recorder.py
```
This will start the server and it will simulate data coming from two different sensors



Start the web application. 

```sh
cd raspberry-backend
python3 app.py
```

Start firefox with the following address:

```sh
firefox 127.0.0.1:5000
```


License
----

For the benefit of everyone.


# Apache
To use with a full production level Apache2 server deployed with mod wsgi, 
use the following instructions. Apache2 should already be installed on raspian

First install the mod wsgi apache component for python 3 and enable
```sh
sudo apt-get install libapache2-mod-wsgi-py3
sudo a2enmode wsgi
```

Add the user pi (or whatever you are using) to the group www-data

```sh
sudo usermod –a -G \"www-data\" pi
```

Now copy our site config to the apache location for available sites and enable it
```sh
sudo cp share/hev.conf /etc/apache2/sites-available/
sudo a2ensite hev.conf
#reload apache
sudo systemctl reload apache2
```
The web page is now served on the default port 80, so you should be able to access on any computer on your local network
