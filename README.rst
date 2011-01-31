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

Or run directly from sources without any install::

   ./run.py

Also you need pygtk to be installed.


Usage
=====

Simply run::

   typetrainer

After start you can click right mouse button at keyboard to activate popup menu.
It contains:

* Tutor generator selector.
* Keyboard selector.
* Recent files list.
* Open file dialog item.

Tutor generator needs utf-8 encoded file to make exercises for you. You should
provide it via command line or activating ``Open`` dialog.

Personally I prefer to run type trainer with fortunes.

TODO
====

* Python tutor.
* Statistic plots.
* Advanced Russian tutor.