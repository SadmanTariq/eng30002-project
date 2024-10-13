import paho.mqtt.client as mqtt
from random import uniform
from time import sleep

from paho.mqtt.enums import CallbackAPIVersion

import config


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    client.subscribe("grid/+/generation")
    client.subscribe("grid/+/consumption")
    client.subscribe("price/+")


grids = {}

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    if not msg.topic.startswith("grid/"):
        # Ignore messages that are not about grids
        return
    
    _, grid_name, value_type = msg.topic.split("/", 2)

    if grid_name not in grids:
        grids[grid_name] = {"generation": 0, "consumption": 0}

    grids[grid_name][value_type] = float(msg.payload)

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
