import paho.mqtt.client as mqtt
import json
import time

def on_message(client, userdata, message) :
    msg_decoced = str(message.payload.decode("utf-8", "ignore"))
    m_in=json.loads(msg_decoced)
    print(m_in)
    print("Received message:{} on topic{}".format(message.payload, message.topic))

def on_disconnect(client, userdata,rc=0):
    client.loop_stop()

def on_publish(client, userdata, result):
    print("published data is: ")
    pass

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")
 
Connected = False   #global variable for the state of the connection

# Creating the mqtt client
client = mqtt.Client()

# Callback functions
client.on_message = on_message
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_connect = on_connect

# Provides the private key/certificats needed to make a secure connection
#client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt", keyfile="client.key")

# Connect to port 8884 in order to make a secure connection 8884
client.connect("146.169.163.5",port=1883)

#subscribe to that topic
client.subscribe("IC.embedded/GROUP_NAME/#")

# Starts a new thread, that calls the loop method at regular intervals for you.
# It also handles re-connects automatically.
client.loop_start()

while Connected != True:    #Wait for connection
    time.sleep(0.1)
 
try:
    while True:
 
        time.sleep(5)
        dicMessage = {
            "sensor1": [1,2,3,4,5,6],
            "sensor2": [10,20,30,40,50,60]
        }
        client.publish("IC.embedded/GROUP_NAME/test", json.dumps(dicMessage))
 
except KeyboardInterrupt:
 
    client.disconnect()
    client.loop_stop()

#An example of how to publish a msg ot the broket
#MSG_INFO = client.publish("IC.embedded/GROUP_NAME/test","hello")

#print(mqtt.error_string(MSG_INFO.rc))