#!/bin/bash
# bootstrap dscreen
if [ $(id) -eq "0" ]; then
  echo "you are not root this is required"
  exit 1
fi
sudo apt update -y && sudo apt upgrade -y
sudo apt install git RPi.GPIO python3 python3-pip -y
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz

git clone https://github.com/climbtheworld/dscreen
cd dscreen
pip install -r requirements.txt
crontab -l > cron_dscreen
echo "SHELL=/bin/bash
0,24,27,30 5,6,7,8,* * * * cd /home/pi/e-paper && python test-dscreen.py 2&1 >logger" >> cron_dscreen
crontab cron_dscreen
rm cron_dscreen