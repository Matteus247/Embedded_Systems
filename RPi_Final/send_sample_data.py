import paho.mqtt.client as mqtt
import json
import time

broker_ip = "146.169.153.141"

def on_disconnect(client, userdata, rc=0):
    client.loop_stop()

client = mqtt.Client()
print("created client")
print(client.connect("146.169.153.141", port=1883))
client.subscribe("IC.embedded/GROUP_NAME/#")
client.loop_start()
client.on_disconnect = on_disconnect

with open('e5_heel_d.txt', 'r') as f:
    d = f.readlines()
with open('e5_heel_t.txt', 'r') as f:
    t = f.readlines()
for i in range(len(d)):
    d[i] = float(d[i])
for i in range(len(t)):
    t[i] = float(t[i])

with open('e5_toe_d.txt', 'r') as f:
    d1 = f.readlines()
with open('e5_toe_t.txt', 'r') as f:
    t1 = f.readlines()
for i in range(len(d)):
    d1[i] = float(d1[i])
for i in range(len(t)):
    t1[i] = float(t1[i])

with open('e5_spin_d.txt', 'r') as f:
    d2 = f.readlines()
with open('e5_spin_t.txt', 'r') as f:
    t2 = f.readlines()
for i in range(len(d)):
    d2[i] = float(d2[i])
for i in range(len(t)):
    t2[i] = float(t2[i])

MQTT_dict = {
                "eventID": 0,
                "heel_data": d,
                "heel_time": t,
                "toe_data": d1,
                "toe_time": t1,
                "spin_data": d2,
                "spin_time": t2
            }

print("created dict")
json_obj = json.dumps(MQTT_dict)
print("created JSON")
MSG_INFO = client.publish("IC.embedded/GROUP_NAME/test", json_obj)
print(mqtt.error_string(MSG_INFO.rc))

time.sleep(5)