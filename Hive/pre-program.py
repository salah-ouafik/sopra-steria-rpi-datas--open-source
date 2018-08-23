#! /usr/bin/python

"""Copyright 2018 SopraSteria.
This work is licensed under my intership in SopraSteria"""

__author__="Ouafik Poideddine"
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
    print('Connected to Adafruit IO!  Listening for Poid changes...')
    # Subscribe to changes on a feed named Poid.
    client.subscribe('Poid')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print('Feed {0} received new value: {1}'.format(feed_id, payload))


# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

client.loop_background()
# Now send new values every 15 seconds.
print('Publishing a new message every 15 seconds (press Ctrl-C to quit)...')
while True:
    value = random.randint(50, 100)
    print('Publishing {0} to Poid.'.format(value))
    client.publish('Poid', value)
    sleep(5)

#client.loop_blocking()

