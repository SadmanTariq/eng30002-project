import paho.mqtt.client as mqtt

import rsa
from paho.mqtt.enums import CallbackAPIVersion

from sys import argv

import config

# If -e is passed in, the data will be encrypted
ENCRYPT = "-e" in argv
PRIVKEY = rsa.PrivateKey.load_pkcs1(config.PRIVATE_KEY, "PEM")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    client.subscribe("grid/+/generation")
    client.subscribe("grid/+/consumption")
    client.subscribe("price/+")


grids = {}


def decrypt(data: bytes):
    return rsa.decrypt(data, PRIVKEY).decode()


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    if not msg.topic.startswith("grid/"):
        # Ignore messages that are not about grids
        return
    
    _, grid_name, value_type = msg.topic.split("/", 2)

    if grid_name not in grids:
        grids[grid_name] = {"generation": 0, "consumption": 0}

    payload = msg.payload
    if ENCRYPT:
        payload = decrypt(payload)
    payload_value = float(payload.split(": ")[-1])

    grids[grid_name][value_type] = payload_value

    # Calculate and publish price
    client.publish(f"price/{grid_name}", get_price(grids[grid_name]["generation"], grids[grid_name]["consumption"]))


def get_price(generation, consumption):
    # Arbitrary credits based on ratio of consumption to generation
    try:
        return consumption / generation 
    except ZeroDivisionError:
        return -1


mqttc = mqtt.Client(CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(config.BROKER, config.PORT, 60)
mqttc.loop_forever()
