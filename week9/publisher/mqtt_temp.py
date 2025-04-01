import os
import glob
import time
import paho.mqtt.client as mqtt
from gpiozero import LED

# --- Setup unique ID ---
id = "jarvy-76f3"  # Replace this with a GUID or something unique
client_name = id + "_temperature_client"

# --- MQTT Setup ---
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect("192.168.28.183")
mqtt_client.loop_start()
print("MQTT connected!")

# --- LED Setup --- My GPIO 17 is not working properly
green_led = LED(18)

# --- DS18B20 Sensor Setup ---
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]  # Grab first temp sensor
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
        temp_c = float(temp_string) / 1000.0
        return temp_c
    return None

# --- Main loop ---
try:
    while True:
        temp = read_temp_celsius()
        print(f"Temperature: {temp:.2f}°C")

        if temp > 25:
            green_led.on()
        else:
            green_led.off()

        time.sleep(3)

except KeyboardInterrupt:
    print("\nProgram interrupted. Exiting...")

finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    green_led.off()
    print("Clean exit.")
