#!/bin/bash

echo "UltimMC installer for Raspberry Pi (64 bit)"

sleep 2

echo "Updating package definitions..."

sudo apt update

echo "Installing dependencies"

sudo apt install build-essential libopenal1 x11-xserver-utils subversion git clang cmake curl zlib1g-dev openjdk-11-jdk qtbase5-dev mesa-utils

echo "Cloning source code..."

cd "$HOME"

git clone --recursive https://github.com/UltimMC/Launcher UltimMC

cd UltimMC

mkdir build

cd build

echo "Generating Makefiles..."

cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DJAVA_HOME='/usr/lib/jvm/java-11-openjdk-arm64' -DLauncher_META_URL:STRING="https://raw.githubusercontent.com/theofficialgman/meta-multimc/master-clean/index.json" ..

echo "Compiling UltimMC..."

make -j$(nproc) install

echo "Installation is complete. Please download and extract an aarch64 java 8 jre tarball from https://adoptium.net/en-GB/marketplace/"
