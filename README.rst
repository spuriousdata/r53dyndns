======================
r53dyndns
======================

r53dyndns is a django app that lets you manage your own dynamic dns server
using amazon route53 as the dns server.


###############
INSTALLATION
###############

    python ./setup.py install


in settings.py
Add `r53dyndns` to INSTALLED_APPS
Add an ApiKey, Zone, and Domain in the django admin.

-----------------------
Usage
-----------------------

curl -X POST -d "apikey=abcdefghijklmnopqrstuvwxyz" http://mysite.com/update/foo.example.com/

-------------------
DEPENDS
-------------------
django 1.5+
boto

