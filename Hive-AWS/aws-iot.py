import json
import random
import datetime
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

topic='/sbs/ruchedata/'
client='iot-ruche-data'
path='/home/pi/Desktop/Hive-AWS/Certifs/'

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
    
time.sleep(2) #wait for 2 secs

# generate Weight values
def getWeightValues():
    data = {}
    data['deviceValue'] = random.randint(70, 100)
    data['deviceParameter'] = 'Weight'
    data['deviceId'] = random.choice(deviceNames)
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

# generate External Temperature values
def getExtTemperatureValues():
    data = {}
    data['deviceValue'] = random.randint(15, 37)
    data['deviceParameter'] = 'ExternalTemperature'
    data['deviceId'] = random.choice(deviceNames)
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

# generate Internal Temperature values
def getIntTemperatureValues():
    data = {}
    data['deviceValue'] = random.randint(25, 40)
    data['deviceParameter'] = 'InternTemperature'
    data['deviceId'] = random.choice(deviceNames)
    data['temperatureDeviceId'] = random.choice(temperatureDeviceNames)
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

# generate Humidity values
def getHumidityValues():
    data = {}
    data['deviceValue'] = random.randint(50, 90)
    data['deviceParameter'] = 'Humidity'
    data['deviceId'] = random.choice(deviceNames)
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

# generate Balance values
def getBalanceValues():
    data = {}
    data['deviceValue'] = random.randint(-1,1)
    data['deviceParameter'] = 'Balance'
    data['deviceId'] = random.choice(deviceNames)
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

# Generate each parameter's data input in varying proportions
while True:
    time.sleep(1)
    rnd = random.random()
    if (0 <= rnd < 0.20):
        data = json.dumps(getWeightValues())
        print(data)
        myMQTTClient.publish(topic+'weight', data, 0) #publish the payload
        
    elif (0.20<= rnd < 0.55):
        IntData = json.dumps(getIntTemperatureValues())
        print(IntData)
        myMQTTClient.publish(topic+'intemperature', IntData, 0) #publish the payload
        time.sleep(1)
        ExtData = json.dumps(getExtTemperatureValues())
        print(ExtData)
        myMQTTClient.publish(topic+'extemperature', ExtData, 0) #publish the payload
    elif (0.55<= rnd < 0.70):
        data = json.dumps(getHumidityValues())
        print(data)
        myMQTTClient.publish(topic+'humidity', data, 0) #publish the payload
    else:
        data = json.dumps(getBalanceValues())
        print(data)
        myMQTTClient.publish(topic+'balance', data, 0) #publish the payload

