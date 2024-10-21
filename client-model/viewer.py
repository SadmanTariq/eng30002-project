import paho.mqtt.client as mqtt
import os

from paho.mqtt.enums import CallbackAPIVersion
import config

from sys import argv
import rsa

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
    match msg.topic.split("/", 1)[0]:
        case "grid":
            _, grid_name, value_type = msg.topic.split("/", 2)

            if grid_name not in grids:
                grids[grid_name] = {"generation": 0, "consumption": 0, "price": 0}

            payload = msg.payload
            if ENCRYPT:
                payload = decrypt(payload)
            payload_value = float(payload.split(": ")[-1])

            grids[grid_name][value_type] = payload_value
        case "price":
            _, grid_name = msg.topic.split("/", 1)
            if grid_name not in grids:
                grids[grid_name] = {"generation": 0, "consumption": 0, "price": 0}
            grids[grid_name]["price"] = float(msg.payload)

    os.system("cls" if os.name == "nt" else "clear")
    for n, g in grids.items():
        print_grid(n, g)
        print()


def print_grid(name, grid):
    print(f"{name}:")
    print(f"  Generation: {grid['generation']}")
    print(f"  Consumption: {grid['consumption']}")
    print(f"  Price: {grid['price']}")

mqttc = mqtt.Client(CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(config.BROKER, config.PORT, 60)
mqttc.loop_forever()
