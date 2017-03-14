#!/bin/bash
echo "configure"
echo "START at:" $(date)
echo "00 01 * * * root /usr/bin/python /home/ubuntu/bem_analytic/querydata.py >> /var/log/fl13data.log" | tee --append /etc/cron.d/cubemswasted
echo "00 02 * * * root /usr/bin/php /var/www/html/fl13wasted_lab.php >> /var/log/fl13wasted.log" | tee --append /etc/cron.d/cubemswasted
echo "05 02 * * * root /usr/bin/php /var/www/html/fl13wasted_lecturer.php >> /var/log/fl13wasted.log" | tee --append /etc/cron.d/cubemswasted
echo "*/5 * * * * /usr/bin/php /var/www/html/checkidaasfl13.php >> /var/log/checkidaas.log" | tee --append /etc/cron.d/checkidaas
echo "FINISH at:" $(date)
echo "##########FINISHED############"
