#!/bin/bash

echo "HI"
sudo systemctl stop collabradoodle

cd `dirname "${BASH_SOURCE[0]}"`
echo "Directory: " `pwd`
GIT_DIR=`pwd`/.git git pull

sudo systemctl start collabradoodle
