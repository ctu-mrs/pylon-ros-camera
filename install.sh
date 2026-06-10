#!/bin/bash

# check if script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

FILENAME_SDK=pylon_26.03.1-deb0_amd64.deb
NASMRS_LINK_SDK=https://nasmrs.fel.cvut.cz/index.php/s/rQjRwRKjHj1CEA6/download

FILENAME_SUPP=pylon-supplementary-package-for-blaze-1.7.3.73dbe706a_amd64.deb
NASMRS_LINK_SUPP=https://nasmrs.fel.cvut.cz/index.php/s/bV58ZwVr0v243b0/download

# get ROS version
distro=`lsb_release -r | awk '{ print $2 }'`
[ "$distro" = "24.04" ] && ROS_DISTRO="jazzy"

# rc file
if [ $SHELL = /usr/bin/zsh ]; then
SHELL_TYPE=zsh
elif [ $SHELL = /bin/bash ]; then
SHELL_TYPE=bash
fi

RCFILE=.${SHELL_TYPE}rc

TMPDIR=$(mktemp -d)

wget --no-check-certificate -O $TMPDIR/$FILENAME_SDK $NASMRS_LINK_SDK
wget --no-check-certificate -O $TMPDIR/$FILENAME_SUPP $NASMRS_LINK_SUPP

apt update
apt install -y libxcb-cursor0
apt install -y $TMPDIR/$FILENAME_SDK
apt install -y $TMPDIR/$FILENAME_SUPP
