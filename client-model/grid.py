import paho.mqtt.client as mqtt
from random import uniform
from time import sleep

from sys import argv

from paho.mqtt.enums import CallbackAPIVersion

import config

if len(argv) != 4:
    print("Usage: python grid.py <name> <mean generation> <mean consumption>")
    exit(1)

NAME = argv[1]
GENERATION = float(argv[2])
CONSUMPTION = float(argv[3])


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


mqttc = mqtt.Client(CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
# mqttc.on_message = on_message

mqttc.connect(config.BROKER, config.PORT, 60)
mqttc.loop_start()


def get_random(v: float):
    # Return a random value between 0.9 and 1.1 times the input value
    return v * uniform(0.9, 1.1)


while True:
    mqttc.publish(f"grid/{NAME}/generation", get_random(GENERATION))
    mqttc.publish(f"grid/{NAME}/consumption", get_random(CONSUMPTION))

    print(f"grid/{NAME}/generation", get_random(GENERATION))
    print(f"grid/{NAME}/consumption", get_random(CONSUMPTION))

    # Sleep for 5 seconds with a random factor
    sleep(uniform(0.9, 1.1) * 5)
