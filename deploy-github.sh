#!/bin/sh

./build.py

cd output
echo "Commit message:" `date`
git add *
git commit -am "`date`"
git push
