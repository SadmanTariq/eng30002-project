import paho.mqtt.client as mqtt
import threading
import time
import random
import json
import signal
import sys

BROKER = "raspberrypi.local"
PORT = 1883
TOPIC = "iot/devices"


# Handling Ctrl+C to stop the script
def signal_handler(sig, frame):
    print("Stopping client...")
    stop_event.set()
    for client, thread in clients:
        client.disconnect()
        thread.join()
    sys.exit(0)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Client {userdata} connected to broker")
        client.connected_flag = True
    else:
        print(f"Failed to connect, return code {rc}")
        client.connected_flag = False


def on_disconnect(client, userdata, rc):
    client.connected_flag = False


def on_publish(client, userdata, mid):
    print(f"Data from {userdata} successfully published.")


def publish_data(client, ClientId):
    while not stop_event.is_set():
        if client.connected_flag:
            # Generate random microgrid data
            voltage = round(random.uniform(220.0, 240.0), 2)  # in Volts
            current = round(random.uniform(10.0, 50.0), 2)  # in Amps
            power_output = round(voltage * current, 2)  # in Watts
            energy_consumed = round(random.uniform(0.1, 10.0), 2)  # in kWh
            frequency = round(random.uniform(49.0, 51.0), 2)  # in Hz

            payload = json.dumps(
                {
                    "ClientId": ClientId,
                    "voltage": voltage,
                    "current": current,
                    "power_output": power_output,
                    "energy_consumed": energy_consumed,
                    "frequency": frequency,
                }
            )

            client.publish(TOPIC, payload)
            time.sleep(1)
        else:
            time.sleep(1)


def start_device(ClientId):
    client = mqtt.Client(userdata=ClientId)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.connected_flag = False
    client.connect(BROKER, PORT)
    client.loop_start()

    thread = threading.Thread(target=publish_data, args=(client, ClientId))
    thread.start()

    return client, thread


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    ClientIds = ["client_1"]
    stop_event = threading.Event()
    clients = []
    for ClientId in ClientIds:
        client, thread = start_device(ClientId)
        clients.append((client, thread))
    while True:
        time.sleep(1)
