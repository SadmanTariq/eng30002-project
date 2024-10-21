import paho.mqtt.client as mqtt
import json
import time
from collections import defaultdict
import signal
import sys

# Constants
RATE_LIMIT = 10  # Messages per second per client
CLIENT_ACCESS = {"client_1": "client_1"}  # Simple authentication

# Tracking message count for rate limiting
message_count = defaultdict(int)
last_reset = time.time()


# Handling Ctrl+C to stop the script
def signal_handler(sig, frame):
    print("Shutting down server...")
    client.disconnect()
    sys.exit(0)


# Rate limiter function
def rate_limiter(client_id):
    global last_reset
    current_time = time.time()
    if current_time - last_reset > 1:
        last_reset = current_time
        message_count.clear()

    if message_count[client_id] >= RATE_LIMIT:
        return False
    message_count[client_id] += 1
    return True


def on_authenticate(client, username, password):
    if CLIENT_ACCESS.get(username) == password:
        return True
    else:
        return False


# MQTT Connect callback
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("iot/devices")


# MQTT Message callback
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        ClientId = payload.get("ClientId")

        # Check rate limit
        if not rate_limiter(ClientId):
            return

        # Extract microgrid data
        voltage = payload.get("voltage")
        current = payload.get("current")
        power_output = payload.get("power_output")
        energy_consumed = payload.get("energy_consumed")
        frequency = payload.get("frequency")

        # Print received data
        print(f"Received data from {ClientId}:")
        print(
            f"Voltage: {voltage}V, Current: {current}A, Power: {power_output}W, Energy: {energy_consumed}kWh, Frequency: {frequency}Hz\n"
        )
    except Exception as e:
        print(f"Invalid data received: {e}")


# Create an MQTT client, set authentication, and assign callbacks
client = mqtt.Client()

# Enable authentication with username/password
client.username_pw_set("client_1", "client_1")

client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect("localhost", 1883)

# Start the loop to process incoming messages
client.loop_start()

# Capture Ctrl+C to stop the server
signal.signal(signal.SIGINT, signal_handler)

# Keep the server running
while True:
    time.sleep(1)