#! /usr/bin/python

"""Copyright 2018 SopraSteria.
This work is licensed under my intership in SopraSteria"""

__author__="Ouafik Salaheddine"
__version__="1.0.0"
__date_0_ ="26/07/2018 19:00h"

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
    print('Connected to Adafruit IO!  Listening for poid changes...')
    # Subscribe to changes on a feed named poid.
    client.subscribe('poid')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

table=[]
table=[0,1,2,3]
poidRuche=0
def flushData(client):
    for x in range(0,3):
        index1 = random.randint(0,3)
        index2 = random.randint(0,3)
        value1 = random.randint(20,70)
        value2 = random.randint(20,70)
    
        table[index1]= value1
        table[index2]= value2
        
        for i in range(0,4):
            print('Publishing {0} to poid.'.format(table[i]))
            client.publish('poid', table[i])
        poidRuche=table[0]
        for i in range(1,4):
            poidRuche+= table[i]
        print('poid ruche : {0} '.format(poidRuche))
        sleep(10)
    return poidRuche
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
poidRuche=flushData(client)
print('poid ruche externa : {0} '.format(poidRuche))
sleep(10)
print('finish')
    
#client.loop_blocking() //so the code will still be running in background : it's useful for just listening to events and invoke ....


