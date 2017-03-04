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
keyfile="/var/www/html/key.ini"
echo "[keyid]" | tee $keyfile
echo "num_swipe='$num_swipeid'" | tee --append $keyfile
echo "num_user='$num_userid'" | tee --append $keyfile
echo "kinect='$kinectid'" | tee --append $keyfile
echo "exports.TempLower='$TempLower';" | tee --append /home/ubuntu/echonetlite/device.info
echo "exports.TempSet='$TempSet';" | tee --append /home/ubuntu/echonetlite/device.info
echo "exports.ipself='$private_echonet';" | tee --append /home/ubuntu/echonetlite/device.info
echo "FINISH at:" $(date)
echo "##########FINISHED############"
