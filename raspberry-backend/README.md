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



# Apache
To use with a full production level Apache2 server deployed with mod wsgi, 
use the following instructions. Apache2 should already be installed on raspian

First install the mod wsgi apache component for python 3 and enable
```sh
sudo apt-get install libapache2-mod-wsgi-py3
#disable first in case we have a python2 version enabled
sudo a2dismode wsgi
sudo a2enmode wsgi
```

Add the user pi (or whatever you are using) to the group www-data

```sh
sudo usermod –a -G "www-data" pi
```

Now copy our site config to the apache location for available sites and enable it
```sh
#update the locations in hev.conf if needed
sudo cp share/hev.conf /etc/apache2/sites-available/
#disable default location
sudo a2dissite 000-default.conf
#enable our hev site
sudo a2ensite hev.conf
#reload apache
sudo systemctl reload apache2
```
The web page is now served on the default port 80, so you should be able to access on any computer on your local network.
Note that the hev server must be running when apache is started or the page won't load, as it throws an error. It can be restarted with
```sh
sudo systemctl reload apache2
```

## For Apache on Redhat derived platforms, for example Fedora and Centos: 

Install apache2 (called httpd) and wsgi to allow python apps to run 
servered by apache. Note you will have had to add EPEL (extra packages 
for enterprise linux) to your repositories first. 

```sudo yum install httpd httpd-devel 
pip3 install mod-wsgi 
``` 

Note I am using python3.8 which I complied myself (the default python3 
is 3.4 which is too early a version) so if the line above fails 
recompile python with 
```./configure --enable-shared --prefix=/usr/local 
LDFLAGS=-Wl,-rpath=/usr/local/lib && make altinstall``` 
then install mod-wsgi 
```sudo /usr/local/pip3.8 install mod-wsgi``` 

Add wgsi to apache 
```/usr/local/bin/mod_wsgi-express install-module > 02-wsgi.conf && sudo 
mv 02-wsgi.conf /etc/httpd/conf.modules.d/02-wsgi.conf``` 

Start apache (note use `enable` to make this permanent): 
```sudo systemctl start httpd``` 

Check it is working: 
```firefox http://localhost/``` 
Should see a page with "Testing 123.. " in big letters at the top. 

Check the user and group apache runs under (default is `apache` for both): 
```grep -E "^User|^Group" /etc/httpd/conf/httpd.conf``` 

Add the owner of the directory containing hev-sw (username) in to the 
apache group (or other group if different above): 
```sudo usermod -aG apache username``` 

Log the user "username" out and back in to propagate the new group 
membership. 

Modify the file `{PATH_TO_FILES}/hev-sw/raspberry-backend/share/hev.conf` to 
match the required users, groups and path to files. Also change the 
Errorlog and CustomLog lines (Redhat and Debian derived distributions 
have different configurations here): 

```<VirtualHost *:80> 
WSGIDaemonProcess hev user=username group=apache threads=1 
WSGIScriptAlias / {PATH_TO_FILES}/hev-sw/raspberry-backend/hev.wsgi 
<Directory "{PATH_TO_FILES}/hev-sw/raspberry-backend/"> 
WSGIProcessGroup hev 
WSGIScriptReloading On 
WSGIApplicationGroup %{GLOBAL} 
Require all granted 
</Directory> 
ErrorLog "logs/hev_error_log" 
CustomLog "logs/hev_access_log" combined 
</VirtualHost> 
WSGIRestrictStdout Off 
``` 

Set all files in `{PATH_TO_FILES}\hev-sw` to group `apache` so wgsi can 
access them: 
```cd {PATH_TO_FILES}/hev-sw 
find . | xargs chgrp apache 
``` 
Fix the home directory of username so that apache can list the files: 
```chmod +x /home/username``` 

Add configuration to httpd 
```cp {PATH_TO_FILES}/hev-sw/raspberry-backend/shar/hev.conf 
/etc/httpd/conf.d/``` 
Restart httpd to reload conf: 
```sudo systemctl reload httpd``` 

Stop the SELINUX protection: by default files outside /var/html can not 
be read by apache: 
```sudo setenforce 0 && sudo sestatus``` 

Add the required modules to python3 the code needs: 
```sudo /usr/local/bin/pip3 install Flask chardet``` 

Start the data server 
```cd {PATH_TO_FILES}/hev-sw/raspberry-dataserver/ ; python3 
hevserver.py -i share/sample.txt``` 

Then (finally) you'll be able to start the display running: 
```firefox http://localhost/``` 


License
----

For the benefit of everyone.
