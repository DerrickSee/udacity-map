Udacity Catalog App
=============

This is an application with basic authentication and the ability to CRUD categories and items.

Dependencies
------------
Vagrant is required. Installation details can be found at https://www.vagrantup.com/.


Run Application Locally
-----------------------
1. Within the project directory, run vagrant.
```
vagrant up
```
2. Initiate bower install to download bower components
```
cd /vagrant/catalog
bower install
```
3. Create tables in Database by in shell
```python
from catalog import db
db.create_all()
```
4. Run Application
```
python catalog.py
```
5. Visit application at http://localhost:5000 on a browser to view application.
