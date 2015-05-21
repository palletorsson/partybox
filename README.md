Partybox
========

* login into the PI using ssh
ssh pi@192.169.0.100 ()

Installation: 
* $ sudo apt-get update
* $ sudo apt-get install virtualenv
* $ virtualenv dataparty
* $ cd dataparty 
* $ source bin/activate 
* $ git clone https://github.com/palletorsson/partybox.git
* $ cd partybox
* $ pip install -r requirements.txt 
* $ cd partybox
* $ python manage.py runserver
* (edit settings.py)

* error: decoder jpeg not available
** install libjpeg-dev with apt:
** sudo apt-get install libjpeg-dev
** need to do sudo apt-get update

* to be able to extract sound data from mp3:
sudo apt-get install python-hachoir-metadata
sudo apt-get install python-hachoir-core

* install supervisor
* 

* runing gunicorn
gunicorn partybox.wsgi:application

* create initial data
manage.py loaddata initialdata.json


gunicorn_django --workers=3 --bind 127.0.0.1:8000

