#!/bin/bash
useddisk=$(df -h | awk '$1 == "/dev/sda1" {print $5}' | sed -e 's/[%]//g' )
useddiskg=$(df -h | awk '$1 == "/dev/sda1" {print $3}' | sed -e 's/[%]//g' )
diskspace=$(df -h | awk '$1 == "/dev/sda1" {print $4}' | sed -e 's/[%]//g' )
diskhigh=80
checkflag="/home/tsrlee/disk.info"
echo $useddisk
if [ $useddisk -gt $diskhigh ]; then
	echo ABNORMAL
	STATUS=$(head -1 $checkflag)
	echo $STATUS
	if [ $STATUS -eq 0 ] && [ $useddisk -gt $diskhigh ]; then
		echo "send line"
	curl -X POST -H 'Authorization: Bearer XSqjX9VEY3KJFrpPDEInT16M3BMz1EI4gJaFB3f8G2j' -F "message=disk space of $(hostname) over $useddisk %" https://notify-api.line.me/api/notify
		echo 1 > $checkflag
	elif [ $STATUS -eq 1 ] && [ $useddisk -gt $diskhigh ]; then
		echo 1 > $checkflag
		echo "Not send line"
	elif [ $STATUS -eq 1 ] && [$useddisk -lt $diskhigh ]; then
		echo 0 > $checkflag
	fi
else
	echo NORMAL
	echo 0 > $checkflag
fi
echo "#########################"
