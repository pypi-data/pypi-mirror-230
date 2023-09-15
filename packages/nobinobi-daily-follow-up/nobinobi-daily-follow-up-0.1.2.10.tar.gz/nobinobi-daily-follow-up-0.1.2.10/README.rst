=============================
Nobinobi Daily Follow-Up
=============================

.. image:: https://badge.fury.io/py/nobinobi-daily-follow-up.svg
    :target: https://badge.fury.io/py/nobinobi-daily-follow-up

.. image:: https://travis-ci.org/prolibre-ch/nobinobi-daily-follow-up.svg?branch=master
    :target: https://travis-ci.org/prolibre-ch/nobinobi-daily-follow-up

.. image:: https://codecov.io/gh/prolibre-ch/nobinobi-daily-follow-up/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/prolibre-ch/nobinobi-daily-follow-up

.. image:: https://pyup.io/repos/github/prolibre-ch/nobinobi-daily-follow-up/shield.svg
     :target: https://pyup.io/repos/github/prolibre-ch/nobinobi-daily-follow-up/
     :alt: Updates

.. image:: https://pyup.io/repos/github/prolibre-ch/nobinobi-daily-follow-up/python-3-shield.svg
     :target: https://pyup.io/repos/github/prolibre-ch/nobinobi-daily-follow-up/
     :alt: Python 3

Module Daily follow-up for nobinobi

Documentation
-------------

The full documentation is at https://nobinobi-daily-follow-up.readthedocs.io.

Quickstart
----------

Install Nobinobi Daily Follow-Up::

    pip install nobinobi-daily-follow-up

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'phonenumber_field',
        'crispy_forms',
        'django_extensions',
        'rest_framework',
        'rest_framework.authtoken',
        'rest_framework_datatables',
        'menu',
        'bootstrap_modal_forms',
        'widget_tweaks',
        'django_select2',
        'bootstrap_datepicker_plus',
        'nobinobi_core',
        'nobinobi_staff',
        'nobinobi_child.apps.NobinobiChildConfig',
        'nobinobi_daily_follow_up.apps.NobinobiDailyFollowUpConfig',
        ...
    )

Add Nobinobi Daily Follow-Up's URL patterns:

.. code-block:: python


    from nobinobi_core import urls as nobinobi_core_urls
    from nobinobi_staff import urls as nobinobi_staff_urls
    from nobinobi_child import urls as nobinobi_child_urls
    from nobinobi_daily_follow_up import urls as nobinobi_daily_follow_up_urls


    urlpatterns = [
        ...
        path('', include(nobinobi_core_urls)),
        path('', include(nobinobi_staff_urls)),
        path('', include(nobinobi_child_urls)),
        path('', include(nobinobi_daily_follow_up_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
