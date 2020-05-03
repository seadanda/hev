#!/bin/bash

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
