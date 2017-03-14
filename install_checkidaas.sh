#!/bin/bash
echo "STEP1: INSTANTIATE Check IDaaS"
echo "START at:" $(date)
NSCL_START_TIME=$(date)
myhome=${HOME}
cp /usr/share/zoneinfo/Asia/Bangkok /etc/localtime
bash -c "echo $private1 `cat /etc/hostname` >> /etc/hosts"
wget -q --tries=10 --timeout=20 --spider  http://archive.ubuntu.com
if [[ $? -eq 0 ]]; then
        echo "Server can connect to Internet"
else
        echo "Server cannot connect to Internet"
fi
sudo apt-get update
sudo apt-get install apache2 curl python python-pip python-dev build-essential -y
echo "ServerName $(hostname)" | tee --append /etc/apache2/apache2.conf
apt-get install -y php libapache2-mod-php php-mcrypt php-cli php7.0-gd php7.0-xml* php7.0-curl
systemctl restart apache2 
pip install numpy pandas suds logging uuid datetime
keyfile="/var/www/html/key.ini"
echo "[keyid]" | tee $keyfile
echo "num_swipe='$num_swipeid'" | tee --append $keyfile
echo "num_user='$num_userid'" | tee --append $keyfile
echo "kinect='$kinectid'" | tee --append $keyfile
echo "linenotify='$linenotify'" | tee -append $keyfile
ifconfig ens3 $private_bems1 netmask 255.255.255.0
route add -net 192.168.9.0/24 gw 10.0.14.1
route add -net 10.0.14.0/24 gw 10.0.14.1
route add -net 192.168.90.0/24 ens3
route add -host 161.200.90.122 ens3
#route add -net 161.200.90.0/24 gw 10.0.14.1
route add -net 91.189.88.0/24 gw 10.0.14.1
echo "FINISH at:" $(date)

echo "##########FINISHED############"
