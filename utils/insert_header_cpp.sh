#!/bin/bash

sed -i  "1{
r licence_header_cpp.txt
h;d
};2{H;g;}" $1
