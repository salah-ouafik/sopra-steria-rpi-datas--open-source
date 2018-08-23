    elif (0.20<= rnd < 0.55):
        IntData = json.dumps(getIntTemperatureValues())
        print(IntData)
        myMQTTClient.publish(topic+'intemperature', IntData, 0) #publish the payload
        time.sleep(1)
        ExtData = json.dumps(getExtTemperatureValues())
        print(ExtData)
        myMQTTClient.publish(topic+'extemperature', ExtData, 0) #publish the payload


#! /usr/bin/python

"""Copyright 2018 SopraSteriaThis work is licensed under my intership in SopraSteria"""

__author__="Ouafik Salaheddine"
__version__="2.0.0"
__date__ ="01/08/2018 09:35h"

#Basic imports
import sys
import json
import random
import datetime
import time

#AWS Amazon specific imports
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.Bridge import Bridge, BridgeGain
from Phidgets.Phidget import PhidgetLogLevel

#External Temperature sensor specific imports
from ds18b20 import DS18B20

#Internal Temperature sensor specific imports
# *****************Add the corresponding librairie here ! ************** #


topic='/sbs/realruchedata/'
client='iot-ruche-data'
path='/home/pi/Desktop/Hive-AWS/Certifs/'
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

#Connect to the cloud
myMQTTClient = AWSIoTMQTTClient(client)
myMQTTClient.configureEndpoint("ap6thgx18rs03.iot.us-west-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials(path+'CA.pem'
                                  , path+'edadfb6205-private.pem.key',
                                  path+'edadfb6205-certificate.pem.crt'
                                  )
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

time.sleep(2) #wait for 2 secs

deviceNames = ['Ruche01', 'Ruche02', 'Ruche03', 'Ruche04', 'Ruche05']
temperatureDeviceNames = ['Matrice01', 'Matice02', 'Matrice03', 'Matrice04', 'Matrice05']
#Matrice = la valeur moyenne de la température entre les 2 cadres

connecting_time = time.time() + 10

if time.time() < connecting_time:  #try connecting to AWS for 10 seconds
    myMQTTClient.connect()
    myMQTTClient.publish(topic, "connected", 0)
    print("MQTT Client connection success!")
else:
    print("Error: Check your AWS details in the program")

#create external temperature sensor variable
exTemperatureSensor = DS18B20()

#create internal temperature sensor variable
inTemperatureSensor = 0 #PUT THE REAL FUNCTION HERE !!

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
    return rounds(Gx,2)

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

def getWeightValues(weight):
    data = {}
    data['deviceValue'] = weight
    data['deviceParameter'] = 'Weight'
    data['deviceId'] = random.choice(deviceNames)
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

# generate Balance values
def getBalanceValues(balance):
    data = {}
    data['deviceValue'] = balance
    data['deviceParameter'] = 'Balance'
    data['deviceId'] = random.choice(deviceNames)
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

def getExtTemperatureValues(exTemperatureSensor):
    data = {}
    data['deviceValue'] = exTemperatureSensor
    data['deviceParameter'] = 'ExternalTemperature'
    data['deviceId'] = random.choice(deviceNames)
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

def getInTemperatureValues(inTemperatureSensor):
    data = {}
    data['deviceValue'] = random.randint(25, 40) #put inTemperatureSensor instead of this arbitrarie generated value
    data['deviceParameter'] = 'InternTemperature'
    data['deviceId'] = random.choice(deviceNames)
    data['temperatureDeviceId'] = random.choice(temperatureDeviceNames)
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

def SendJsonData(RawData,subTopic)
    data = json.dumps(RawData)
    print(data)
    myMQTTClient.publish(topic+subTopic, data, 0) #publish the payload
# QoS =0 : no quality of serviice is done in this program

def flushData():
    poidRuche=table[0]
    for i in range(1,4):
        poidRuche+= table[i]
    Gx=centreGx(table,poidRuche)
    Gy= centreGy(table,poidRuche)
    position= gestionPosition(Gx,Gy)    
    SendJsonData(getWeightValues(poidRuche),'weight')
    SendJsonData(getBalanceValues(Gx),'balance0X')
    SendJsonData(getBalanceValues(Gy),'balance0Y')
    SendJsonData(getBalanceValues(position),'position')
    SendJsonData(getInTemperatureValues(exTemperatureSensor),'exTemperatureSensor')
    SendJsonData(getInTemperatureValues(inTemperatureSensor),'inTemperatureSensor')
    
    
    
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
    time.sleep(2)

    print("Set Gain to 8...")
    bridge.setGain(0, BridgeGain.PHIDGET_BRIDGE_GAIN_8)
    time.sleep(2)

    print("Enable the Bridge input for reading data...")
    bridge.setEnabled(0, True)
    time.sleep(2)

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
#Time Break until we connect to the server
time.sleep(2)

#Now send values every 1 minute
while True:
    flushData()
    time.sleep(60)


    