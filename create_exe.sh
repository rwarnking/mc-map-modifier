#!/bin/bash
# Remove init.py since it interferes with the pyinstaller
rm src/__init__.py
# https://stackoverflow.com/questions/44573861/
# https://pyinstaller.org/en/stable/hooks.html
pyinstaller -F --hidden-import nbt.world --additional-hooks-dir=. src/application.py
for entry in "dist"/*
do
  echo "$entry"
done
