#!/bin/bash
useddisk=$(df -h | awk '$1 == "/dev/sda1" {print $5}' | sed -e 's/[%]//g' )
useddiskg=$(df -h | awk '$1 == "/dev/sda1" {print $3}' | sed -e 's/[%]//g' )
diskspace=$(df -h | awk '$1 == "/dev/sda1" {print $4}' | sed -e 's/[%]//g' )
curl -X POST -H 'Authorization: Bearer XSqjX9VEY3KJFrpPDEInT16M3BMz1EI4gJaFB3f8G2j' -F "message=disk space usage of '$(hostname)' = $useddisk % ( $useddiskg/$diskspace)" https://notify-api.line.me/api/notify
#XSqjX9VEY3KJFrpPDEInT16M3BMz1EI4gJaFB3f8G2j
