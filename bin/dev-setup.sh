#!/bin/bash

echo 'installing serverless framework'
npm install --global serverless

echo 'installing serverless packages'
npm install

echo 'creating python virtualenv'
virtualenv --python=`which python3` .venv

echo 'installing packages into virtualenv'
source .venv/bin/activate
pip install -r requirements.txt
pip install -r dev-requirements.txt

echo 'Virtualenv created and requirements installed'
echo 'Please run `source .venv/bin/activate` in your current shell'
