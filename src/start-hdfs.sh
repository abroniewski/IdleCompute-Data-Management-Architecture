#!/bin/bash
clear
printf "\n Starting NDFS for you \n\n"

cd /opt/homebrew/Cellar/hadoop/3.3.2/libexec/sbin
./start-all.sh

printf "\n Up and running! \n\n"

jps
