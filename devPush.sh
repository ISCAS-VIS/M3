#!/bin/sh
###########################
cd ./
# switch to branch you want to use
git checkout dev
# add all added/modified files
git add .
# commit changes
read commitMessage
now = date +"%Y-%m-%d %H:%M:%S"
git commit -am "[$now] $commitMessage"
# push to git remote repository
git push origin dev
###########################
echo "Press Enter..."
read