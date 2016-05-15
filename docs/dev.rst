Setup a development enviroment
========================================

This document is a guide to install an enviroment
to contribute to the development of Sur library. It's fully based on modern
Ubuntu Linux distributions (particularly Ubuntu 15.10) but should be
straight forward follow this on any other linux distribution.


Install system packages
------------------------

1. Install system packages::

      $ sudo apt-get install git python-dev python-pip wine gfortran \
                            g++ libfreetype6-dev libpng12-dev xclip
      $ sudo pip install virtualenvwrapper


.. note::

    To code, of course you'll also need an editor. Could be anyone you prefer!
    Some people prefers simple ones like ``gedit`` (installed by default)
    or geany. Some other prefers something more geeky like ``vim``
    or even more complete tools like ``pydev`` or ``ninja-ide``.


Make a virtual enviroment
-------------------------

We use virtualenv_ (using virtualenvwrapper_) to
isolate our enviroment for other projects and system-wide python packages

2. Setup virtualenvwrapper

   2.1  Create a directory to hold your virtualenvs::

     mkdir ~/.virtualenvs
     mkdir ~/projects
     mkdir ~/.pip_download_cache

   2.2  Edit you ``~/.bashrc`` adding these lines::

     export WORKON_HOME=$HOME/.virtualenvs
     source /usr/local/bin/virtualenvwrapper.sh
     export PROJECT_HOME=$HOME/projects      #folder for new projects. Could be what you want

  2.3  And reload that::

    $ source ~/.bashrc

3. Now create the project sur::

    $ mkproject sur

  This will create a new virtualenv in the WORKON_HOME binded to a
  project directory in PROJECT_HOME

.. note::

    Next times, when you want to active the sur's virtualenv you'll run::

        $ workon sur

    When you want to deactive the virtualenv, on any path ::

        (sur)~/projects/sur$ deactivate

Checkout the code
-----------------

sur's git repo isn't public, so you need to have credentials to read
and/or write it. Please if you don't have a Bitbucket account, create one:

1. Go to https://bitbucket.org/account/signup/ and sign up

2. Let me know (gaitan@gmail.com) your username
   and ask for dev permissions on Sur. If you don't have an user
   on bitbucket also let me know first. I'll send and invitation

3. Setup a ssh-key_ ::

    $ ssh-keygen
    $ xclip -sel clip < ~/.ssh/id_rsa.pub

    and paste this on
    https://bitbucket.org/account/user/<your_userr>/ssh-keys/

4. Then we go::

    (sur)~/projects/sur$ git clone git@bitbucket.org:phasety/envelope-sur.git .
    (sur)~/projects/sur$ git checkout develop

5. Remember to configure your identity (so, your future great code will
   be recognized)::

    (sur)$ git config --global user.name "Juan Perez"
    (sur)$ git config --global user.email perez@phasety.com


Install in dev mode
-------------------

    (sur)~/projects/sur$ pip install -U numpy pip jupyter nose
    (sur)~/projects/sur$ pip install -e .

.. tip::

    The flag ``-e`` on the last command means this package will be *editable*.
    Every change on the code of Sur will impact automatically.
    It's the same than ``python setup.py develop``


Then check if it was installed::

    (sur) $ ipython

    In [1]: import sur    # may take few seconds to load


Run tests::

    (sur) $ nosetests


And open an example notebook for lib usage::

    (sur) $ jupyter notebook examples/basic_envelope.ipynb


**¡Happy coding!**

.. _virtualenv: http://www.virtualenv.org
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/
.. _ssh-key: https://confluence.atlassian.com/pages/viewpage.action?pageId=270827678
.. _numpy: http://numpy.org/
.. _matplotlib: http://matplotlib.org/


