#!/usr/bin/env python


import sys
sys.path.append("..")
from utilities import packetmaker
from send import send


""" A python script that creates and sends a time request. """ 

msg = packetmaker.make_time_packet()
print 'Time request packet made...' 

send(msg)