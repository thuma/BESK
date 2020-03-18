#!/bin/sh
pytest --flake8
if [ $? -eq 1 ]
then
    echo "Ingen deploy p.g.a. fallerade tester"
else
    ssh besk.kodcentrum.se -l besk -A "cd BESK; git pull; sudo systemctl restart besk; sudo systemctl status besk;"
fi
