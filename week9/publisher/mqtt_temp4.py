import os
import glob
import time
import json
import paho.mqtt.client as mqtt
from gpiozero import LED

# --- ID and topics ---
id = "jarvy-76f3"  # Must match the one in app.py
client_name = id + "_temperature_client"
telemetry_topic = id + "/telemetry"
command_topic = id + "/commands"

# --- LED setup ---
green_led = LED(18)

# --- DS18B20 Sensor setup ---
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

# --- Handle command from server ---
def handle_command(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        led_on = payload.get("led_on", False)
        print(f"Received command: {payload}")

        if led_on:
            green_led.on()
        else:
            green_led.off()
    except Exception as e:
        print("Error processing command:", e)

# --- MQTT setup ---
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect("localhost")  # or IP of the broker
mqtt_client.loop_start()

# --- Subscribe to command topic ---
mqtt_client.subscribe(command_topic)
mqtt_client.on_message = handle_command

# --- Main loop: Send telemetry every 3 sec ---
try:
    while True:
        temp = read_temp_celsius()
        print(f"Temperature: {temp:.2f}°C")
        payload = {"temperature": temp}
        mqtt_client.publish(telemetry_topic, json.dumps(payload))
        time.sleep(3)

except KeyboardInterrupt:
    print("\nInterrupted. Cleaning up...")

finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    green_led.off()
    print("Clean exit.")
