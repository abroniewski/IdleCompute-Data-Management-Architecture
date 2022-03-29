#!/bin/bash
clear
printf "\n Shutting down NDFS for you \n\n"

cd /opt/homebrew/Cellar/hadoop/3.3.2/libexec/sbin
./stop-all.sh

printf "\n All done \n\n"

jps
