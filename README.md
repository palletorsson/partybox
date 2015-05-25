Partybox
========

* Prepare your Raspberry PI with a SD card with a RASPBIAN
* Boot and expand filesystem, reboot

Installation of the webserver:

* Login into the PI using ssh ( user:pi password:raspberry )

MySql:
* $ sudo apt-get update 
* $ sudo apt-get install mysql-server ( I use the password:raspberry )
* $ mysql -u root -p
* CREATE DATABASE partybox;
* exit
* $ sudo apt-get install libmysqlclient-dev

Pip and Partybox:
* $ sudo apt-get install python-pip
* $ sudo apt-get install python-dev 
* $ sudo apt-get install libjpeg-dev
* $ git clone https://github.com/palletorsson/partybox.git
* $ cd partybox
* $ sudo pip install -r requirements.txt 
* $ cd partybox

Create database tables:
* $ python manage.py syncdb
* (create a user pi password:raspberry)

Import initial data:
* $ python manage.py loaddata initialdata.json

Test run server:
* $ python manage.py runserver

 
To be able to extract sound data from mp3 install:
* $ sudo apt-get install python-hachoir-metadata
* $ sudo apt-get install python-hachoir-core

For securing start on boot and restart install Supervisor:
* $ sudo apt-get install supervisor
* $ sudo nano /etc/supervisor/conf.d/flask_project.conf

Add these lines:

<pre>
[program:partybox]
command = gunicorn_django --workers=3 --bind 127.0.0.1:8000
directory = /home/pi/partybox/partybox/
user = pi
</pre>

Exit and save and restart your pi 

Install nginx:



* Setup the the wifi-network as a honeypot. This will allow anyone with Wi-Fi on their laptop or phone to connect to the PI using the SSID "partyBox" and in the end it will allow of interaction with the local server. 

* See Instructions here:
* https://github.com/palletorsson/network_setup_partybox

