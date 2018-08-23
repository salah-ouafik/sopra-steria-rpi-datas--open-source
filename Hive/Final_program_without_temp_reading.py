#! /usr/bin/python

"""Copyright 2018 SopraSteria.
This work is licensed under my intership in SopraSteria"""

__author__="Ouafik Salaheddine"
__version__="1.0.0"
__date__ ="26/07/2018 19:00h"

#Basic imports
import sys
from time import sleep
import random
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.Bridge import Bridge, BridgeGain
from Phidgets.Phidget import PhidgetLogLevel


# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

# Set to your Adafruit IO key.
ADAFRUIT_IO_KEY = 'c527e85da54a4d8cab58f70de6a7d7f3'

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = 'salahEo'

#offset value
OFFSET_VALUE = 0 #Put the real value here after executing the
#offset determiner (BridgeSimple.py) , don't put the Hive in the base

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
    table[e.index] = COEFFICIENT_VALUE*(e.value - OFFSET_VALUE)
    
def connected(client):
    print('Connected to Adafruit IO!  Listening for changes...')
    # Subscribe to changes on a feed named Weight.
    for feed_id in ['poidruche' , 'gx' , 'gy' , 'position']:
        client.subscribe(feed_id)


def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    
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


def flushData(client):
    poidRuche=table[0]
    for i in range(1,4):
        poidRuche+= table[i]
    print('Publishing {0} to PoidRuche.'.format(poidRuche))
    client.publish('poidruche', poidRuche)
    Gx=centreGx(table,poidRuche)
    Gy= centreGy(table,poidRuche)
    position=gestionPosition(Gx,Gy)
    print('Publishing {0} to Gx.'.format(Gx))
    client.publish('gx', Gx)
    print('Publishing {0} to Gy.'.format(Gy))
    client.publish('gy', Gy)
    print('Publishing {0} to Position.'.format(position))
    client.publish('position', position)
    
# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
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

# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

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
!# The first option is to run a thread in the background so you can continue
# doing things in your program.
client.connect()
client.loop_background()
sleep(10)
#Now send values every 1 minute
while True:
    flushData(client)
    sleep(60)

