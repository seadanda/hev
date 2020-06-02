#!/bin/bash
a2dismod wsgi
a2enmod wsgi
#update the locations in hev.conf if needed
#disable default location
a2dissite 000-default.conf
#enable our hev site
a2ensite hev.conf
#reload apache
sudo systemctl reload apache2