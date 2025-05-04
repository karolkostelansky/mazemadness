#!/bin/bash

for LINE in $(ps | grep -v grep | grep client\.py | awk '{ print $1 }'); do
  kill -SIGINT "$LINE"
  sleep 1
done
