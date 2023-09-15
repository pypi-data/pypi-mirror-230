ckanext-dc_log_view
===================

|PyPI Version| |Build Status| |Coverage Status|


A CKAN log viewer for DC files.

Installation
------------

::

    pip install ckanext-dc_log_view



Add this extension to the plugins and defaul_views in ckan.ini:

::

    ckan.plugins = [...] dc_log_view
    ckan.views.default_views = [...] dc_log_view


Testing
-------
If CKAN/DCOR is installed and setup for testing, this extension can
be tested with pytest:

::

    pytest ckanext

Testing can also be done via vagrant in a virtualmachine using the
`dcor-test <https://app.vagrantup.com/paulmueller/boxes/dcor-test/>` image.
Make sure that `vagrant` and `virtualbox` are installed and run the
following commands in the root of this repository:

::

    # Setup virtual machine using `Vagrantfile`
    vagrant up
    # Run the tests
    vagrant ssh -- sudo bash /testing/vagrant-run-tests.sh


.. |PyPI Version| image:: https://img.shields.io/pypi/v/ckanext.dc_log_view.svg
   :target: https://pypi.python.org/pypi/ckanext.dc_log_view
.. |Build Status| image:: https://img.shields.io/github/actions/workflow/status/DCOR-dev/ckanext-dc_log_view/check.yml
   :target: https://github.com/DCOR-dev/ckanext-dc_log_view/actions?query=workflow%3AChecks
.. |Coverage Status| image:: https://img.shields.io/codecov/c/github/DCOR-dev/ckanext-dc_log_view
   :target: https://codecov.io/gh/DCOR-dev/ckanext-dc_log_view
