#!/bin/bash

sudo rmmod nvidia_uvm
sudo nvidia-modprobe -u
sudo systemctl restart ollama
pg_ctl -D db start
streamlit run ragdemo.py 