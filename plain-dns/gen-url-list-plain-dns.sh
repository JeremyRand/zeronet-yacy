#!/bin/bash

ncdumpzone --ncdumpzone.format=url-list | sort --unique | tee url-list-plain-dns.txt
cat url-list-plain-dns.txt | sort --random-sort | tee url-list-random-plain-dns.txt
