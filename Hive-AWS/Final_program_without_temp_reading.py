#! /usr/bin/python

"""Copyright 2018 SopraSteriaThis work is licensed under my intership in SopraSteria"""

__author__="Ouafik Salaheddine"
__version__="2.0.0"
__date__ ="01/08/2018 09:35h"

#Basic imports
import sys
from time import sleep
import random
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.Bridge import Bridge, BridgeGain
from Phidgets.Phidget import PhidgetLogLevel

#Offset value
OFFSET_VALUE = 0 #Put the real value here after executing the
#offset determiner (offset_determiner.py)

#Coefficient : Capacity over Rated Output
COEFFICIENT_VALUE = 50

   
#Create an accelerometer object
try:
    bridge = Bridge()
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)

#Event Handler Callback Functions
def BridgeAttached(e):
    attached = e.device
    print("Bridge %i Attached!" % (attached.getSerialNum()))

def BridgeDetached(e):
    detached = e.device
    print("Bridge %i Detached!" % (detached.getSerialNum()))

def BridgeError(e):
    try:
        source = e.device
        print("Bridge %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
#contient les valeurs qui seront lu 
table = [0,0,0,0]

def BridgeData(e):
    source = e.device
    print("Bridge %i: Input %i: %f" % (source.getSerialNum(), e.index, e.value))
    #e.index varies between 0 and 3 
    table[e.index] = COEFFICIENT_VALUE*(e.value - OFFCET_VALUE)

def centreGx(table,poidRuche):
    Gx=((table[2]+table[3])-(table[0]+table[1]))/poidRuche
    return round(Gx,2)

def centreGy(table,poidRuche):
    Gy=((table[0]+table[3])-(table[1]+table[2]))/poidRuche
    return round(Gy,2)

def gestionPosition(Gx,Gy):
    position=-1
    if(Gx*Gy>0):
        if Gx>=0 :
            position=3
        else:
            position=1
    else:
        if Gx<0 :
            position=0
        else:
            position=2
    return position


def flushData():
    poidRuche=table[0]
    for i in range(1,4):
        poidRuche+= table[i]
    Gx=centreGx(table,poidRuche)
    Gy= centreGy(table,poidRuche)
    position=gestionPosition(Gx,Gy)
    
    
# Setup the callback functions defined above.

try:
	#uncomment to generate a log file ( For testing puroses only)
    #bridge.enableLogging(PhidgetLogLevel.PHIDGET_LOG_VERBOSE, "phidgetlog.log")
	
    bridge.setOnAttachHandler(BridgeAttached)
    bridge.setOnDetachHandler(BridgeDetached)
    bridge.setOnErrorhandler(BridgeError)
    bridge.setOnBridgeDataHandler(BridgeData)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)
 
#Main Program Code
    
print("Opening phidget object....")

try:
    bridge.openPhidget()

    print("Waiting for attach....")

    bridge.waitForAttach(10000)
    
    print("Set data rate to 8ms ...")
    bridge.setDataRate(16)
    sleep(2)

    print("Set Gain to 8...")
    bridge.setGain(0, BridgeGain.PHIDGET_BRIDGE_GAIN_8)
    sleep(2)

    print("Enable the Bridge input for reading data...")
    bridge.setEnabled(0, True)
    sleep(2)

except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        bridge.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    print("Exiting....")
    exit(1)
sleep(10)

#Now send values every 1 minute
while True:
    flushData()
    sleep(60)

