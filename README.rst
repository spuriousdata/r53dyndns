======================
r53dyndns
======================

r53dyndns is a tool running on flask that lets you manage your own dynamic dns
server using amazon route53 as the dns server.

**********************
WARNING
**********************

This software is in beta. The server seems to work fine, but the cli needs some
work. Use at your own risk.


###############
INSTALLATION
###############

::

    python ./setup.py install


###############
SETUP
###############

::
    
    $ r5dadmin initdb
    OK
    
    $ r5dadmin addowner bob
    abcdefghijklmnopqrstuvwxyz

    $ r5dadmin addzone -o bob -a aws_access_key -s aws_secret_key -z ABCDEF123 -A 1.2.3.4 example.com
    OK

    $ r5dadmin adddomain -o bob foo.example.com
    OK

-----------------------
Usage
-----------------------

On your clients cron something like::

    curl -X POST -d "apikey=abcdefghijklmnopqrstuvwxyz" http://my-r53dndns-site.com/update/foo.example.com/

-------------------
DEPENDS
-------------------
boto3 1.4.4+
Flask 0.12+

