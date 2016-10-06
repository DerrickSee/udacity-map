Udacity Map/Brooklyn App
=============

This is an application using Google Maps and Yelp API.

Dependencies
------------
Vagrant is required. Installation details can be found at https://www.vagrantup.com/.


Run Application Locally
-----------------------
1. Within the project directory, run vagrant.
```
vagrant up
```
2. Connect to vagrant box and export your Yelp API Credentials
```
vagrant ssh
export APP_ID = <YELP_APP_ID>
export APP_SECRET = <YELP_APP_SECRET>
```

4. Run Application
```
cd /vagrant/brooklyn
python brooklyn.py
```
5. Visit application at http://localhost:5000 on a browser to view application.


Catalog API
-----------
To access catalog json endpoint, go to http://localhost:5000/api/catalog.json
