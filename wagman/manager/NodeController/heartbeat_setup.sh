#!/bin/bash

cd /sys/class/gpio
echo 204 > export
cd gpio204
echo out > direction
