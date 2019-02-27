# Button Game API
This is a backend designed for [Button Game](https://github.com/Natsku123/Button-Game).

## API

| URL | METHOD | DESCRIPTION | PARAMETERS |
|-----|--------|-------------|------------|
|/api/|GET|Root of api future documentation|NONE|
|/api/v1.0/players/|GET|Get one player if username exists else all players|username|
|/api/v1.0/click/|POST|Send click to server with 'username' in body|NONE|
|/api/v1.0/needed-clicks/|GET|Get next goal and amount of clicks needed|NONE|

## Installation guide

NOTE: Most of these commands need to be run with `root` or `sudo`.

Install needed programs:
```bash
apt-get install mariadb-server uwsgi nginx
```

Install needed libraries for python:
```bash
pip3 install flask flask-cors pymysql
```

Installer can be downloaded by clicking [this link](https://dl.meckl.in/button-game-api/install.py).

or with:
```bash
wget https://dl.meckl.in/button-game-api/install.py
```

But first you need to create a directory and a database with a user for this.

Access the mysql with your root and its password (set in the installation of mariadb)
```bash
mysql -u root -p
```

Create database and a user for it.
```mysql
CREATE DATABASE button_game;
GRANT ALL PRIVILEGES ON button_game.* TO 'api-user'@'localhost' IDENTIFIED BY 'very nice password';
FLUSH PRIVILEGES;
```

Now create a directory that will contain the api software itself.
```bash
mkdir /var/www/button-game-api
```

Now you should copy your just downloaded installer with wget:
```bash
cp install.py /var/www/button-game-api/install.py
```

or download it now:
```bash
cd /var/www/button-game-api
wget https://dl.meckl.in/button-game-api/install.py
```

Now you are ready to install!

Run the installer:
```bash
python3 install.py
```
And give the installer all the needed stuff that you just set up.

If you are using something else than Ubuntu, you should add this line in your `config/uwsgi.ini` file below `module = wsgi`:
```bash
plugins = logfile, python36
```
Replace python36 with python35 if you are using python3.5 and so on.

Create a new service to run the API:
```bash
nano /etc/systemd/system/button-game-api.uwsgi.service
```

Paste this inside with your own directories.
```bash
[Unit]
Description=uWSGI Backend for Button Game
After=syslog.target

[Service]
WorkingDirectory=/var/www/button-game-api
# Can require modifying, based on uwsgi installation directory
ExecStart=/usr/bin/uwsgi --ini config/uwsgi.ini
# Requires systemd version 211 or newer
RuntimeDirectory=uwsgi
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```

Enable the service:
```bash
systemctl daemon-reload
```

Start the service:
```bash
service button-game-api.uwsgi start
```

If everything went right (without errors) you can now start to setup Nginx.

```bash
nano /etc/nginx/uwsgi_params
```

And paste parameters from [this page](https://github.com/nginx/nginx/blob/master/conf/uwsgi_params) .

Create configuration for Nginx:
```bash
nano /etc/nginx/sites-available/button-game-api.conf
```

And fill it with this:
```bash
server {
    listen 80;
    server_name api.example-game.com www.api.example-game.com;
    root /var/www/button-game-api/;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/var/www/button-game-api/config/uwsgi.sock;
    }
}
```

Enable your configuration:
```bash
ln -s /etc/nginx/sites-available/button-game-api.conf /etc/nginx/sites-enabled/button-game-api.conf
```

Test that your configuration works:
```bash
nginx -t
```

If it works:
```bash
service nginx reload
```

Or:
```bash
service nginx restart
```

Now setup your domain to point to your servers IP-address.

To fix permission issues (caused byt using root or sudo):
```bash
cd ..
chown www-data:www-data button-game-api/ -R
```

### Setup SSL (optional)

Download certbot (if you are using something other than Ubuntu 14.04 - 18.04, installation guide can be found [here](https://certbot.eff.org/)):
```bash
apt-get update
apt-get install software-properties-common
add-apt-repository universe
add-apt-repository ppa:certbot/certbot
apt-get update
apt-get install certbot python-certbot-nginx
```

Get SSL certificates from Let's Encrypt:
```bash
certbot --nginx
```
Now select your newly created site.