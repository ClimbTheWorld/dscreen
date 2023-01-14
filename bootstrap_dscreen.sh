#!/bin/bash
# bootstrap dscreen
if [[ "$EUID" -ne 0 ]]; then
  echo "you are not root this is required"
  exit 1
fi
if [[ ! -f "first" ]]; then
  echo "Start first part of installation"
  sudo apt update -y && sudo apt upgrade -y
  sudo apt install git python3-rpi.gpio python3 python3-pip -y
  sed -i "s/#dtparam=spi=on/dtparam=spi=on/g" /boot/config.txt
  touch first
  reboot
else
  echo "Start second part of installation"
  wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
  tar -zxvf bcm2835-1.60.tar.gz
  cd bcm2835-1.60
  ./configure
  make
  make check
  make install
  cd ..

  pip install -r requirements.txt
  crontab -l > cron_dscreen
  echo "SHELL=/bin/bash \
0,24 * * * * cd /home/pi/e-paper && python dscreen.py 2&1 >logger" >> cron_dscreen
  crontab cron_dscreen
  rm -f cron_dscreen
  
  git clone https://github.com/ClimbTheWorld/dscreen
  cd dscreen
  rm -f first
fi