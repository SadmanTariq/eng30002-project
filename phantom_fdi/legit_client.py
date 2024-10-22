import paho.mqtt.client as mqtt
import random
import time

def publish_legitimate_data():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect("localhost", 1883, 60)
    while True:
        value = random.uniform(0.9, 1.1)  
        client.publish("test/topic", value)
        print(f"Legit data published: {value}")
        time.sleep(5) 

publish_legitimate_data()
