import numpy as np
import serial
import time
import paho.mqtt.client as paho

###################################################################################################

# First, set up XBee connection
serdev = '/dev/ttyUSB0'
s = serial.Serial(serdev, 9600)

s.write("+++".encode())
char = s.read(2)
print("Enter AT mode.")
print(char.decode())

s.write("ATMY 0x136\r\n".encode())
char = s.read(3)
print("Set MY 0x136.")
print(char.decode())

s.write("ATDL 0x236\r\n".encode())
char = s.read(3)
print("Set DL 0x236.")
print(char.decode())

s.write("ATID 0x1\r\n".encode())
char = s.read(3)
print("Set PAN ID 0x1.")
print(char.decode())

s.write("ATWR\r\n".encode())
char = s.read(3)
print("Write config.")
print(char.decode())

s.write("ATMY\r\n".encode())
char = s.read(4)
print("MY :")
print(char.decode())

s.write("ATDL\r\n".encode())
char = s.read(4)
print("DL : ")
print(char.decode())

s.write("ATCN\r\n".encode())
char = s.read(3)
print("Exit AT mode.")
print(char.decode())

# after XBEE conneted, send RPC command to ask for the acc data
print("start sending RPC\r\n")
time.sleep(5)
s.write("/myled1/write 0\r".encode())
time.sleep(1)
s.close()

###################################################################################################

# collect the data from K66F

Fs = 100.0;  # sampling rate
Ts = 1.0/Fs; # sampling interval
y = np.arange(0,1,Ts) # signal vector; create Fs samples



serdev = '/dev/ttyACM0'
s = serial.Serial(serdev, 115200)
for x in range(0, int(Fs)): # get 100 data
    line=s.readline() # Read an echo string from K66F terminated with '\n'
    # print line
    y[x] = float(line)
s.close()
print("collecting data finished!")
time.sleep(1)
###################################################################################################

#MQTT publisher
mqttc = paho.Client()
# Settings for connection

host = "localhost"
topic= "Velocity"
port = 1883

# Callbacks
def on_connect(self, mosq, obj, rc):
    print("Connected rc: " + str(rc))

def on_message(mosq, obj, msg):
    print("[Received] Topic: " + msg.topic + ", Message: " + str(msg.payload) + "\n");

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed OK")

def on_unsubscribe(mosq, obj, mid, granted_qos):
    print("Unsubscribed OK")

# Set callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

# Connect and subscribe
print("Connecting to " + host + "/" + topic)
mqttc.connect(host, port=1883, keepalive=60)
mqttc.subscribe(topic, 0)

for x in range(0, int(Fs)):
    mesg = float(y[x])
    mqttc.publish(topic, mesg)
    print(mesg)
    time.sleep(1)
