#!/bin/sh

find ../typetrainer -name '*.glade' | xargs -n1 intltool-extract --type=gettext/glade -l

xgettext -L Python -k_ -kN_ -o messages.pot --package-name=typetrainer `find ../typetrainer -name '*.py'`
xgettext -k_ -kN_ -j -o messages.pot --package-name=typetrainer ./tmp/*
