#!/bin/bash
echo "START"
echo "START at:" $(date)
/usr/bin/php /var/www/html/checkidaasfl13.php
/usr/bin/php /var/www/html/fl13wasted_lab.php
/usr/bin/php /var/www/html/fl13wasted_lecturer.php
echo "FINISH at:" $(date)
echo "##########FINISHED############"
