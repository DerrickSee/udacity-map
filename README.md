Udacity Map/Brooklyn App
=============

This is an application using Google Maps and Yelp API.

Dependencies
------------
Vagrant is required. Installation details can be found at https://www.vagrantup.com/.

Yelp API credentials is also required. Please register at https://www.yelp.com/developers/.


Run Application Locally
-----------------------
1. Within the project directory, run vagrant.
```
cd vagrant/
vagrant up
```
2. Connect to vagrant box and export your Yelp API Credentials
```
vagrant ssh
export APP_ID=1MzeDvwoIQJOVVpXJm6YJg
export APP_SECRET=CTLK2bTCP16i4L4VghSikXQPldV5OUMYu8uSuCfXu1fpVCmxuWsCFXdzZemXcjL9
```

4. Run Application
```
cd /vagrant/brooklyn
python brooklyn.py
```
5. Visit application at http://localhost:5000 on a browser to view application.
