#!/bin/bash

source /home/${USER}/.bashrc
conda -V
conda activate SimMOL
echo "CONDA ENV: ${CONDA_DEFAULT_ENV}"
echo "date: `date`"

# Init jupyter-lab
nohup jupyter-lab --no-browser --port=8888 --ip=0.0.0.0 &> /tmp/nohup.out & 
pid_jupyterlab=$!

echo "Open using:"
sleep 3
grep "^[[:space:]]*http://$HOSTNAME" /tmp/nohup.out | sed "s/$HOSTNAME:8888/localhost:8889/g"

# In your local machine use:
# ssh -L 8889:SERVER_HOSTNAME:8888 -p 86 -fN USER@SERVER_HOSTNAME


echo "To close the process use:"
echo "    kill ${pid_jupyterlab}"
echo "    kill ${pid_jupyterlab}" >> /tmp/nohup.out
