import os
import glob
import time
import json
import paho.mqtt.client as mqtt

# --- Unique ID and MQTT topic ---
id = "uidthinghere"
client_name = id + "_temperature_client"
telemetry_topic = id + "/telemetry"

# --- MQTT Setup ---
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect("test.mosquitto.org")
mqtt_client.loop_start()
print("MQTT connected!")

# --- DS18B20 Temperature Sensor Setup ---
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temp_celsius():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        return float(temp_string) / 1000.0
    return None

# --- Main loop: Send telemetry every 3 seconds ---
try:
    while True:
        temp = read_temp_celsius()
        print(f"Temperature: {temp:.2f}°C")

        payload = {
            "temperature": temp
        }

        mqtt_client.publish(telemetry_topic, json.dumps(payload))
        print(f"Published to {telemetry_topic}: {payload}")

        time.sleep(3)

except KeyboardInterrupt:
    print("\nInterrupted.")

finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("Clean exit.")
