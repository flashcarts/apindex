#!/usr/bin/bash

echo "installing apindex"
cd
cd .cache
git clone --depth=1 https://github.com/flashcarts/apindex.git
cd apindex
cmake . -DCMAKE_INSTALL_PREFIX=/usr/local
sudo make install
cd ..
rm -rf apindex
