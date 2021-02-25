#!/bin/bash
cd Downloads
wget https://github.com/hex-in/libscrc/archive/v1.6.tar.gz
tar xzf v1.6.tar.gz
cd libscrc-1.6/
python3 setup.py build
sudo python3 setup.py install
