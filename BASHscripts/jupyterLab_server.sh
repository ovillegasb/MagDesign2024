#!/bin/bash

source /home/${USER}/.bashrc
conda -V
conda activate SimMOL
echo "CONDA ENV: ${CONDA_DEFAULT_ENV}"
echo "date: `date`"
# cd /home/${USER}/.notebooks/

rm -vf /tmp/nohup_${USER}.out

# Init jupyter-lab
nohup jupyter-lab --no-browser --port=8888 --ip=0.0.0.0 &> /tmp/nohup_${USER}.out & 
pid_jupyterlab=$!

echo "Wait.."
sleep 10

# In your local machine use:
# ssh -L 8889:SERVER_HOSTNAME:8888 -p 86 -fN USER@SERVER_HOSTNAME

echo "RUN in local terminal:"
echo "ssh -L 8889:yargla.chimie.univ-poitiers.fr:8889 -p 86 -fN user@yargla.chimie.univ-poitiers.fr"

echo "Open using:"
sleep 5
grep "^[[:space:]]*http://$HOSTNAME" /tmp/nohup_${USER}.out | sed "s/$HOSTNAME:8888/localhost:8889/g"

echo "To close the process use:"
echo "    kill ${pid_jupyterlab}"
echo "    kill ${pid_jupyterlab}" >> /tmp/nohup.out
