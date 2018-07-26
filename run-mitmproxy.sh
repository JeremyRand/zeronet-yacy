#!/bin/bash

sudo mitmdump --listen-port=80 --mode=transparent --set flow_detail=0 --scripts ./mitm-script.py
#sudo mitmdump --listen-port=80 --mode=transparent --scripts ./mitm-script.py
