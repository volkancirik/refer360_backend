#!/usr/bin/env/sh

sudo rm /tmp/refer360annotation.nginx.log
sudo rm -rf /var/www/refer360annotation/static
sudo chmod 755 /var/www/refer360annotation/
sudo mkdir -p /var/www/refer360annotation/static
sudo chmod -R 777 /var/www/refer360annotation/static
python manage.py collectstatic
sudo chmod -R 777 /var/www/refer360annotation/static
#sudo chown www-data:www-data -R /var/www/refer360annotation/static
sudo service nginx restart
uwsgi --ini refer360.ini --enable-threads

# cd /etc/nginx/sites-available;  sudo ln -s /projects1/refer_backend/refer360annotation/refer360.conf refer360
# cd /etc/nginx/sites-enabled;  sudo ln -s /projects1/refer_backend/refer360annotation/refer360.conf refer360
