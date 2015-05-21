Partybox
========

* Prepare your Raspberry PI with a SD card with a RASPBIAN
* Boot and expand filesystem, reboot
* Login into the PI using ssh ( user:pi password:raspberry )

Installation: 

MySql:
* $ sudo apt-get update 
* $ sudo apt-get install mysql-server ( password:raspberry )
* $ mysql -u root -p
* CREATE DATABASE partybox;
* $ sudo apt-get install libmysqlclient-dev

Pip and Partybox:
* $ sudo apt-get install python-pip
* $ sudo apt-get install python-dev 
* $ git clone https://github.com/palletorsson/partybox.git
* $ cd partybox
* $ sudo pip install -r requirements.txt 
* $ cd partybox
* $ python manage.py runserver


Error: decoder jpeg not available
* install libjpeg-dev with apt:
* sudo apt-get install libjpeg-dev
* need to do sudo apt-get update

To be able to extract sound data from mp3:
* $ sudo apt-get install python-hachoir-metadata
* $ sudo apt-get install python-hachoir-core

Supervisor for securing start and restart of script. Enter:
* $ sudo apt-get install supervisor 
* $ sudo nano /etc/supervisor/conf.d/flask_project.conf

Add these lines:
* [program:partyboc] 
* command = python media-server.py 
* directory = /home/pi/pi-jockey/ 
* user = pi
Exit and save and restart your pi 

Run gunicorn
* $ gunicorn_django --workers=3 --bind 127.0.0.1:8000

( gunicorn partybox.wsgi:application )

Create initial data
* $ manage.py loaddata initialdata.json



