#!/bin/bash
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



download_dir=/home/pi/Downloads
dev_dir=/home/pi/Development

# Get my build of Qt 5.12
curl -L https://chrisburr.me/hev/opt-Qt5.12.tar.gz > $download_dir/opt-Qt5.12.tar.gz
sudo mkdir -p /opt/Qt5.12
cd /opt/Qt5.12
sudo tar xvf $download_dir/opt-Qt5.12.tar.gz

# Build the sources
cd $dev_dir/hev-display
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_PREFIX_PATH=/opt/Qt5.12/lib/cmake ..
make VERBOSE=1 install -j4

# The server I've been testing with
#git clone git@github.com:chrisburr/hev-sw.git
#git checkout avoid-time-jump

#  the display
echo "LD_LIBRARY_PATH=/opt/Qt5.12/lib QML2_IMPORT_PATH=/opt/Qt5.12/qml QML_IMPORT_PATH=/opt/Qt5.12/qml $dev_dir/hev-display/install/bin/hev-display --opengl" >$dev_dir/hev-display/install/bin/hev-display-opengl.sh
chmod +x $dev_dir/hev-display/install/bin/hev-display-opengl.sh
