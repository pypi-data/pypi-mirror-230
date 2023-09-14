#!/bin/bash
#if [ "$EUID" -ne 0 ]
#  then echo "Please run as root"
#  exit
#fi

if [ ! -d "Python-3.9.16" ]; then
    sudo dnf install pybind11-devel libffi-devel
    wget -O Python3.9.16.tar.xz https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tar.xz
    tar -xf Python3.9.16.tar.xz
fi
cd Python-3.9.16
./configure --enable-optimizationsmake
make -j `nproc`


