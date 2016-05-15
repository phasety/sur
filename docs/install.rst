Install
=======

Sur is still under development (considered in *alpha* stage), but it's ready to experiment with.


.. attention:: By the moment, Sur only works with Python 2.7.x. It may change in future versions.


For Windows users
-----------------

Under Windows, Sur is easily installable via a recent version of [pip](https://pip.pypa.io/en/stable/). It's bundle in recents version of Python.

- Open a command line (Start » Run » ``cmd.exe``) and first, upgrade the version of pip (just in case)::

    pip install -U pip

- Then, in a 32bits OS::


    pip install https://ci.appveyor.com/api/buildjobs/satlj7c3vteww2wi/artifacts/dist/sur-1.0.postf6ee05dfcf5c-cp27-cp27m-win32.whl

- Or for 64 bits::

    pip install https://ci.appveyor.com/api/buildjobs/0yyuyr7mb4skhk1l/artifacts/dist/sur-1.0.postf6ee05dfcf5c-cp27-cp27m-win_amd64.whl

.. Note:: Those links are for the last stable (but still *in develop*) versions. You can try newer ones going to https://ci.appveyor.com/project/mgaitan/envelope-sur » Enviroment (x86 or x64) » Artifacts, and copy the the link to the ``.whl`` file)

For Linux users
---------------

(to do)
