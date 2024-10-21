import paho.mqtt.client as mqtt
import json
import time
import signal
import sys


# Handling Ctrl+C to stop the script
def signal_handler(sig, frame):
    print("Shutting down server...")
    client.disconnect()
    sys.exit(0)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully")
        client.subscribe("iot/devices")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        ClientId = payload.get("ClientId")
        voltage = payload.get("voltage")
        current = payload.get("current")
        power_output = payload.get("power_output")
        energy_consumed = payload.get("energy_consumed")
        frequency = payload.get("frequency")

        print(f"Received data from {ClientId}:")
        print(
            f"Voltage: {voltage}V, Current: {current}A, Power: {power_output}W, Energy: {energy_consumed}kWh, Frequency: {frequency}Hz\n"
        )
    except Exception as e:
        print(f"Invalid data received: {e}")


# Create an MQTT client and assign callbacks
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker (localhost in this case)
client.connect("localhost", 1883)

# Start the loop to process incoming messages
client.loop_start()

# Capture Ctrl+C to stop the server
signal.signal(signal.SIGINT, signal_handler)

# Keep the server running
while True:
    time.sleep(1)