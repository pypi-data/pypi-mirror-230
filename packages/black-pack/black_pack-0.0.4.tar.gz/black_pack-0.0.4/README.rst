##########
black-pack
##########
|TestStatus| |PyPiStatus| |BlackStyle|

|BlackPackLogo|

Linting and structural checking for python-packages.
Black-pack helps you to organize your python-package.
Black-pack is very basic and not meant to support custom structures.
Black-pack only checks if a python-package has a specific structure which the author thinks is 'reasonable practice' and which is now backed into black-pack.
Black-pack is meant to help you keep your various python-packages in 'reasonable' shape with ease.
The name 'black-pack' is becasue black-pack adopts parts of the mindset found in 'black'.

*******
Install
*******

.. code-block::

    pip install black_pack


*********************
Usage on command-line
*********************

.. code-block::

    black-pack /path/to/my/python-package


Black-pack will print a list of errors to stdout when your package differs from black-pack's backed in expectations.



.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |TestStatus| image:: https://github.com/cherenkov-plenoscope/black_pack/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/cherenkov-plenoscope/black_pack/actions/workflows/test.yml

.. |PyPiStatus| image:: https://img.shields.io/pypi/v/black_pack
    :target: https://pypi.org/project/black_pack

.. |BlackPackLogo| image:: https://github.com/cherenkov-plenoscope/black_pack/blob/main/readme/black_pack.svg?raw=True
