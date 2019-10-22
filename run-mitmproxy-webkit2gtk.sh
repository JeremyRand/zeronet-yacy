#!/bin/bash

sudo mitmdump --listen-port=80 --mode reverse:http://127.0.0.1:81/ --set keep_host_header=true --scripts ./mitm-script-webkit2gtk.py
