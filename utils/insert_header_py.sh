#!/bin/bash

sed -i  "2{
r licence_header_py.txt
h;d
};3{H;g;}" $1
