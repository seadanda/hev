#!/bin/bash

download_dir=/home/pi/Downloads/

cd $download_dir
wget https://downloads.arduino.cc/arduino-1.8.12-linuxarm.tar.xz
tar xJf arduino-1.8.12-linuxarm.tar.xz
cd arduino-1.8.12
sudo ./install.sh
./arduino-linux-setup.sh pi
wget https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_ARMv7.tar.gz
tar xzf arduino-cli_latest_Linux_ARMv7.tar.gz
sudo cp ./arduino-cli /usr/local/bin/

