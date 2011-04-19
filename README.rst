==========
Scipyshare
==========

Platform for sharing scientific codes for Python.

.. note::

   All of this is still very much under development!

   Don't expect it to work properly or look nice.

============
Installation
============

You must have Django installed: `<http://www.djangoproject.com/>`_

#. Create databases::

    cd deploy
    python manage.py syncdb

   This will also ask you to create a superuser name and password.

#. Load sample data::

    python manage.py loaddata sample

#. Start webserver::

    python manage.py runserver

#. To edit things,

   #. Log in as an user by going to
      `<http://localhost:8000/user/login/>`_
   #. Use the UI to edit things (NB. heavily under construction at the moment)

   Or,

   #. Log in as a superuser (created above) by going to
      `<http://localhost:8000/admin/>`_
   #. Select the items to edit or create
