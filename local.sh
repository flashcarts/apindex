#!/bin/bash

echo "installing apindex"
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr
sudo make install
cd ..
rm -rf build
