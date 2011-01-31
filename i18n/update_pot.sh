#!/bin/sh

xgettext -j -L Python -k_ -kN_ -o messages.pot --package-name=typetrainer `find ../typetrainer -name '*.py'`
