# Import standard Python libraries.
import sys, signal, platform, time, socket, serial
from datetime import datetime
import paho.mqtt.client as mqtt

myos = platform.system()

# Get device serial number

serial_portname = 'COM4'
baud_rate = 9600

mqtt_topic = 'gasfill'
mqtt_subscription = 'unspecified'
mqtt_hostname = '127.0.0.1'
mqtt_portnum = 9001

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ipv4 = s.getsockname()[0]

print(ipv4)

# Attach a handler to the keyboard interrupt (control-C).
def _sigint_handler(signal, frame):
    print("Keyboard interrupt caught, closing down...")
    if serial_port is not None:
        serial_port.close()

    if client is not None:
       client.loop_stop()
    
    sys.exit(0)

signal.signal(signal.SIGINT, _sigint_handler)

def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected with flags: {flags}, result code: {rc}")

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    # The hash mark is a multi-level wildcard, so this will subscribe to all subtopics of 16223
    client.subscribe(mqtt_subscription)
    return

def on_message(client, userdata, msg):
    print(f"message received: topic: {msg.topic} payload: {msg.payload}")

    # If the serial port is ready, re-transmit received messages to the
    # device. The msg.payload is a bytes object which can be directly sent to
    # the serial port with an appended line ending.
    if serial_port is not None and serial_port.is_open:
        serial_port.write(msg.payload + b'\n')
    return
def on_publish(client, userdata, mid):
     print("mid: "+str(mid))

#----------------------------------------------------------------
# Launch the MQTT network client
client = mqtt.Client(transport='websockets')
client.enable_logger()
client.on_connect = on_connect
client.on_message = on_message
# client.tls_set()
# client.username_pw_set(mqtt_username, mqtt_password)

# Start a background thread to connect to the MQTT network.
client.connect_async(mqtt_hostname, mqtt_portnum, 60)
client.loop_start()

try:
  serial_port = serial.Serial(serial_portname, baudrate=baud_rate, timeout=2.0)
  serial_port.isOpen() # try to open port, if possible print message and proceed with 'while True:'
  print (serial_portname + " is opened!")

except: # if port is already opened, close it and open it again and print message
  print (serial_portname + " in used or close, was closed and opened again!")
  exit()

time.sleep(0.2)

print(f"Entering RPI event loop for {serial_portname}.  Enter Control-C to quit.")

while(True):
    now = datetime.now()
    input = serial_port.readline().decode(encoding='ascii',errors='ignore').rstrip()
    # input = serial_port.readline().decode().strip()
    if len(input) == 0:
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Serial device timed out, no data received.")
    else:
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        print(f"{input}")
        if client.is_connected():
            client.publish(topic=mqtt_topic, payload=input)
        else:
            print("MQTT not connect")