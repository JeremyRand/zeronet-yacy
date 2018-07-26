#!/bin/bash

./ncdumpzone --noncompliance-experiments.zeronet=true --noncompliance-experiments.zeronet-ip4="127.0.0.1" --noncompliance-experiments.only=true --ncdumpzone.format=url-list | sort --unique | tee url-list-zeronet-only.txt
cat url-list-zeronet-only.txt | sort --random-sort | tee url-list-random-zeronet-only.txt
