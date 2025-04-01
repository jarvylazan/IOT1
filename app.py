import json
import time
import paho.mqtt.client as mqtt

# --- Unique ID and topic ---
id = "jarvy-76f3"  # Replace this with your real GUID
client_telemetry_topic = id + "/telemetry"
client_name = id + "_temperature_server"

# --- MQTT Setup (no API version needed in 1.6.1) ---
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect("192.168.28.183")
mqtt_client.loop_start()

# --- Handle incoming telemetry ---
def handle_telemetry(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        print("Message received:", payload)
    except json.JSONDecodeError:
        print("Invalid JSON received.")

mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

# --- Main loop ---
try:
    while True:
        time.sleep(2)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("Clean exit.")
