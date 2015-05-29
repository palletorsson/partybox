RadioGaGa
========

* Prepare your Raspberry PI with an SD card with RASPBIAN:
_ See instructions here: https://www.raspberrypi.org/documentation/installation/installing-images/README.md
* Boot and expand filesystem, change timezone, etc. and reboot
* The setup assumes that how have Linux computer on the same the Pi.

Installation of the MySql, Django Webserver, Nginx:
* Login into the PI using ssh ( user: pi password: raspberry )

Update:
* $ sudo apt-get update

install MySql:
* $ sudo apt-get install mysql-server ( I use the password: raspberry )
* $ mysql -u root -p
* CREATE DATABASE partybox;
* exit
* $ sudo apt-get install libmysqlclient-dev

Pip, Partybox and additional liberies:
* $ sudo apt-get install python-pip
* $ sudo apt-get install python-dev 
* $ sudo apt-get install libjpeg-dev
* $ sudo apt-get install ffmpeg
* $ git clone https://github.com/palletorsson/partybox.git
* $ cd partybox
* $ sudo pip install -r requirements.txt 
* $ cd partybox

Create database tables:
* $ python manage.py syncdb
* (create a user pi password: raspberry)

Import initial data:
* $ python manage.py loaddata initialdata.json

Test run server:
* $ python manage.py runserver

To be able to extract sound data from mp3 install:
* $ sudo apt-get install python-hachoir-metadata
* $ sudo apt-get install python-hachoir-core

For the partybox to start at boot, we install Supervisor:
* $ sudo apt-get install supervisor
* $ sudo nano /etc/supervisor/conf.d/partybox_project.conf

Add these lines:

<pre>
[program:partybox]
command = gunicorn_django --workers=3 --bind 127.0.0.1:8000
directory = /home/pi/partybox/partybox/
user = pi
</pre>

_ Save and exit (Ctrl X y) 

Also install the open source reverse proxy server Nginx:
* $ sudo apt-get intall nginx
* $ sudo nano /etc/nginx/site-available/partybox 

Add these lines:
<pre>
server {
        listen 80; ## listen for ipv4; this line is default and implied

        root /home/pi/partybox/partybox;
        index index.html index.htm;

        # Make site accessible from http://localhost/
        server_name localhost;

        location /static/  { # STATIC URL
                alias /home/pi/partybox/partybox/static/;
        }


        location /media/ { # MEDIA URL
                alias /home/pi/partybox/partybox/media/;
        }


        location / {
                proxy_pass_header Server;
                proxy_redirect off;
                client_max_body_size 100M;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header Host $host;
                proxy_set_header X-Scheme $scheme;
                proxy_connect_timeout 20;
                proxy_read_timeout 20;
                proxy_pass http://127.0.0.1:8000;
        }
        error_page 500 502 503 504 /media/50x.html;
}
</pre>

_ Save and exit (Ctrl X y) 

Restart your pi: 
* $ sudo reboot

If everything works, it is time to setup the WiFi-network as a honeypot. The setup will allow anyone with Wi-Fi on their laptop or phone to connect to the PI using the SSID "partyBox" and share.  

Network setup partybox
======================

* Login into the PI using ssh ( user:pi password: raspberry )

Install hostapd. 
* $ sudo apt-get install hostapd

Setting up a free wifi hotspot:
* $ sudo nano /etc/hostapd/hostapd.conf 

Add these lines:
<pre> 
interface=wlan0
driver=rtl871xdrv
ssid=RadioGaGa
channel=6
auth_algs=1
wmm_enabled=0
</pre>

* The driver you are using depends on what wireless card you use
* I use the driver=rtl871xdrv (but nl80211 is a more common one)

Activate hostapd as default:
* $ sudo nano /etc/default/hostapd

Edit the DAEMON_CONF="":

<pre> 
DAEMON_CONF="/etc/hostapd/hostapd.conf"
</pre>

_ Save and exit (Ctrl X y) 

Here you can do an optional Reboot:
* $ sudo reboot

* See that the Pi start without errors
* Login into the PI using ssh ( user:pi password:raspberry )

Tips: Check hostapd
* $ sudo service hostapd status
* $ sudo hostapd /etc/hostapd/hostapd.conf

Here is how to start, stop, restart hostapd:
* $ /etc/init.d/hostapd start
* $ /etc/init.d/hostapd stop
* $ /etc/init.d/hostapd restart

Setting up a DHCP Server, we will use dnsmasq. In this example, we will use 192.168.10.1 as the Pi:s IP-address and a range 192.168.10.2 to 192.168.10.250 addresses to assign to connecting computers. 

Install Dnsmasq:
* $ sudo apt-get install dnsmasq 
* $ sudo nano /etc/dnsmasq.conf

Add these lines:
<pre>
address=/#/192.168.10.1
interface=wlan0
dhcp-range=192.168.10.1,192.168.10.250,12h
no-resolv
</pre>


_ Save and exit 
* $ sudo service dnsmasq restart

These actions will lock the PI out of internet. To get internet connection back: 

* $ sudo nano /etc/dnsmasq.conf

Add these lines:
<pre>
address=/lan/192.168.10.1
interface=wlan0
dhcp-range=192.168.10.1,192.168.10.250,12h
#no-resolv
server=8.8.8.8

_ Save and exit 
* $ sudo service dnsmasq restart


Here you can do an optional Reboot:
* $ sudo reboot


* See that the Pi start without errors
* Login into the PI using ssh ( user:pi password:raspberry )

Check dnsmasq
* $ sudo service dnsmasq status

Next Step: Define a subnet the wireless card.
* $ sudo nano /etc/network/interfaces

_ Add these lines:
<pre> 
auto lo

iface lo inet loopback
#iface eth0 inet dhcp

iface wlan0 inet static
  address 192.168.10.1
  netmask 255.255.255.0
  broadcast 255.0.0.0

pre-up iptables-restore < /etc/iptables.rules
#pre-up iptables-restore < /etc/iptables.ipv4.nat
</pre>

Edit Iptables firewall to direct outside request to local webserver: 
* $ sudo iptables -F
* $ sudo iptables -i wlan0 -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
* $ sudo iptables -i wlan0 -A INPUT -p tcp --dport 80 -j ACCEPT
* $ sudo iptables -i wlan0 -A INPUT -p udp --dport 53 -j ACCEPT
* $ sudo iptables -i wlan0 -A INPUT -p udp --dport 67:68 -j ACCEPT
* $ sudo iptables -i wlan0 -A INPUT -j DROP
*
* $ sudo sh -c "iptables-save > /etc/iptables.rules"

Tips:
List iptables 
iptables -L -n
iptables -L -v

Now Reboot:
* $ sudo reboot.

Check to see that everything seem to work. You should now be able to log on the free WiFi "partyBox" and start sharing.

I used these references to set up the network:
* http://www.daveconroy.com/turn-your-raspberry-pi-into-a-wifi-hotspot-with-edimax-nano-usb-ew-7811un-rtl8188cus-chipset/
* http://www.daveconroy.com/using-your-raspberry-pi-as-a-wireless-router-and-web-server/
* http://raspberrypihq.com/how-to-turn-a-raspberry-pi-into-a-wifi-router/
* http://elinux.org/RPI-Wireless-Hotspot
* http://andrewmichaelsmith.com/2013/08/raspberry-pi-wi-fi-honeypot/
* https://learn.adafruit.com/setting-up-a-raspberry-pi-as-a-wifi-access-point/install-software
 
Old ideas:

* $ sudo nano /etc/hosts
<pre>
* 127.0.0.1 
</pre>

* $ sudo nano /etc/sysctl.conf

* Add the following line to the bottom of the file:
<pre> 

net.ipv4.ip_forward=1



</pre>

sudo echo "Welcome! Start your Gunicorn" > /usr/share/nginx/www/index.html


-Setting up a isc-dhcp-server (can be used instead of dnsmasq)
-
-* $ sudo apt-get install isc-dhcp-server
-* $ sudo nano /etc/dhcp/dhclient.conf 
-
-<pre> 
-authoritative;
-ddns-update-style none;
-default-lease-time 600;
-max-lease-time 7200;
-log-facility local7;
-
-subnet 192.168.10.1 netmask 255.255.255.0 {
-  range 192.168.10.10 192.168.42.254;
-  option broadcast-address 192.168.42.255;
-  option domain-name-servers 8.8.8.8, 8.8.4.4;
-  option routers 192.168.10.1;
-  interface wlan0;
-}
-</pre>

More ip-tables ideas
#!/bin/sh

echo 1 > /proc/sys/net/ipv4/ip_forward

iptables -F
iptables -t nat -F
iptables -X

iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.10.1:80
iptables -t nat -A POSTROUTING -p tcp -d 192.168.10.1 --dport 80 -j SNAT --to-source 192.168.10.11


* $ sudo iptables -t nat -A PREROUTING -s 192.168.1.0/24 -p tcp --dport 80 -j DNAT --to-destination 192.168.10.1:80
* $ iptables-save > /etc/iptables.up.rules
* $  sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

Reset Ip tables:
* $ sudo iptables -t nat -F


