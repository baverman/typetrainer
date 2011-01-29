from setuptools import setup, find_packages

setup(
    name     = 'typetrainer',
    version  = '0.3.1',
    author   = 'Anton Bobrov',
    author_email = 'bobrov@vl.ru',
    description = 'Typing tutor trainer',
    long_description = open('README.rst').read().replace('https', 'http'),
    zip_safe   = False,
    packages = find_packages(exclude=('tests', )),
    include_package_data = True,
    url = 'http://github.com/baverman/typetrainer',
    entry_points = {
        'gui_scripts': [
            'typetrainer = typetrainer.run:run',
        ]
    },
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Education"
    ],
)
