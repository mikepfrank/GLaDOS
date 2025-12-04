#!/bin/bash
cd $AI_DATADIR
mkdir python
cd python
mkdir -p venv scripts data images temp
python3 -m venv venv
source venv/bin/activate
pip install numpy matplotlib pandas scipy jupyter
