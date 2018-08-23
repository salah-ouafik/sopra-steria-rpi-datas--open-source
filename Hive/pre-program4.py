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

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

# Set to your Adafruit IO key.
ADAFRUIT_IO_KEY = 'c527e85da54a4d8cab58f70de6a7d7f3'

# Set to your Adafruit IO username.
ADAFRUIT_IO_USERNAME = 'salahEo'


# Define callback functions which will be called when certain events happen.
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

def afficheTable(table):
    print('Valeur du tableau :')
    for element in table :
        print(element)

def remplirTable(table):
    index1 = random.randint(0,3)
    index2 = random.randint(0,3)
    value1 = random.randint(30,50)
    value2 = random.randint(30,50)

    table[index1]= value1
    table[index2]= value2

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

table=[0,1,2,3]

def flushData(client):
    remplirTable(table)
    afficheTable(table)
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
    
# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()
client.loop_background()
sleep(10)
    # Now send new values every 15 seconds.
print('Publishing a new message every 10 seconds (press Ctrl-C to quit)...')
for x in range(0,20):
    flushData(client)
    sleep(10)
print('finish')



