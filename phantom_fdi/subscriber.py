import paho.mqtt.client as mqtt

def on_message(message):
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("192.168.0.101", 1883, 60)  
client.subscribe("grid/GRID2/consumption")
client.on_message = on_message
client.loop_forever()
