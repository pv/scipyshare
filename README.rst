========
Scipyard
========

Code snippet and project catalogue for scientific use of Python.


Layout
======

We'll try to follow `these instructions <http://ericholscher.com/projects/django-conventions/>`__.

The code is laid out as follows. Custom Django applications are put in::

    apps/APPNAME/__init__.py
    apps/APPNAME/*.py
    apps/APPNAME/static/APPNAME/**
    apps/APPNAME/templates/APPNAME/*.html
    apps/APPNAME/templates/admin/APPNAME/*.html
    apps/APPNAME/templatetags/*.py
    apps/docs/*

and the main project resides in::

    scipyard

