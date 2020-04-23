#!/bin/bash

sudo raspi-config nonint do_hostname hevpi
sudo raspi-config nonint do_overscan 1
sudo raspi-config nonint do_vnc 0
sudo raspi-config nonint do_wifi_country CH
locale=en_US.UTF-8
layout=us
sudo raspi-config nonint do_change_locale $locale
sudo raspi-config nonint do_configure_keyboard $layout

