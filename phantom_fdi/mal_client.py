import random
import paho.mqtt.client as mqtt
import time

def publish_false_data():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect("192.168.0.101", 1883, 60)
    while True:
        false_consumption = random.uniform(0.1, 0.5)
        false_generation = random.uniform(400, 600)
        
        client.publish("grid/GRID2/consumption", f"consumption: {false_consumption}")
        print(f"False consumption data published - consumption: {false_consumption}")
        
        client.publish("grid/GRID2/generation", f"generation: {false_generation}")
        print(f"False generation data published - generation: {false_generation}")
        time.sleep(0.5)

publish_false_data()


