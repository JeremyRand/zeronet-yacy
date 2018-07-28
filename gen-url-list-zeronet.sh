#!/bin/bash

ncdumpzone --ncdumpzone.format=url-list | sort --unique | tee url-list-zeronet-only.txt
cat url-list-zeronet-only.txt | sort --random-sort | tee url-list-random-zeronet-only.txt
