partybox
========

partybox




thing to install apt-get:

* problem: decoder jpeg not available
** install libjpeg-dev with apt:
** sudo apt-get install libjpeg-dev
** need to do sudo apt-get update



* to be able to extract sound data from mp3:
sudo apt-get install python-hachoir-metadata
sudo apt-get install python-hachoir-core


* runing gunicorn
gunicorn partybox.wsgi:application

* login into the PI using ssh
ssh pi@192.169.0.100

* create initial data
manage.py loaddata initialdata.json


gunicorn_django --workers=3 --bind 127.0.0.1:8000

