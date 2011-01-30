#!/bin/sh

xgettext -k_ -kN_ -o messages.pot --package-name=typetrainer `find ../typetrainer -name '*.py'`
