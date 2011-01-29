Type Trainer
============

.. image:: https://cloud.github.com/downloads/baverman/typetrainer/trainer.png

This small utility allows you to grow your typing skills in soft and
non-annoying manner. It tries to behave closely to proprietary VerseQ
application -- adaptive typing tutor which dynamically changes exercises to help
trainee to learn hard places thoroughly.


Install
=======

The most easy way via pypi::

   pip install typetrainer

or::

   easy_install typetrainer

Or you can install from sources::

   python setup.py build
   sudo python setup.py install

Also you need pygtk to be installed.


Usage
=====

::

   typetrainer -t tutor_package /path/to/file/with/words

Where ``tutor_package`` is one of tutors:

* ``en.basic`` Basic English tutor with small-caps letters, commas and apostrophe.
* ``en.advanced`` English tutor with symbols and all-caps letters.
* ``ru.basic`` Basic Russian tutor with only small-caps letters.

``tutor_package`` may be omitted.

And words file is any text in utf8 encoding.

Personally I prefer to run type trainer with fortunes::

   typetrainer /usr/share/fortune/debian

or::

   typetrainer /usr/share/fortune/cookie


TODO
====

* Python tutor.
