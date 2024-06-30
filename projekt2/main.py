import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
import dht
import random                 # Random number generator
from machine import Pin       # Define pin
import keys                   # Contain all keys used here
import wifiConnection         # Contains functions to connect/disconnect from WiFi 


# BEGIN SETTINGS
# These need to be change to suit your environment
RANDOMS_INTERVAL = 60000    # milliseconds
last_random_sent_ticks = 0  # milliseconds
board_led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W on board led
green_led = Pin(18, Pin.OUT)
yellow_led = Pin(17, Pin.OUT)
red_led = Pin(16, Pin.OUT)
tempSensor = dht.DHT11(machine.Pin(27))     # DHT11 Constructor 
led_status = True

# Callback Function to respond to messages from Adafruit IO
def sub_cb(topic, msg):          # sub_cb means "callback subroutine"
    global led_status
    print((topic, msg))          # Outputs the message that was received. Debugging use.
    if msg == b"ON":             # If message says "ON" ...
        led_status = True        # ... then LEDS on
        board_led.on()
        time.sleep(0.1)
        board_led.off()
    elif msg == b"OFF":          # If message says "OFF" ...
        green_led.off()          # ... then LEDS off
        yellow_led.off()
        red_led.off()
        led_status = False

# Function to measure the values received from the temperature and humidity sensor,
# handles the leds and send data to Adafruit IO MQTT server
def measure_temp_hum():
    global last_random_sent_ticks
    global RANDOMS_INTERVAL
    global led_status

    if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):
        return; # Too soon since last one sent.

    try:
        tempSensor.measure()
        temperature = tempSensor.temperature()
        humidity = tempSensor.humidity()

        if (led_status == True):
            if (temperature > 29 or temperature < 16 or humidity > 60 or humidity < 30):
                green_led.off()
                yellow_led.off()
                red_led.on()
            elif (temperature > 25 or temperature < 18 or humidity > 50 or humidity < 35):
                green_led.off()
                yellow_led.on()
                red_led.off()
            elif (temperature >= 18 and humidity >= 35):
                green_led.on()
                yellow_led.off()
                red_led.off()
            else:
                green_led.off()
                yellow_led.off()
                red_led.off()

        print("Temperature is {} degrees Celsius and Humidity is {}%".format(temperature, humidity))
        print("Publishing: {0} to {1} ... ".format(temperature, keys.AIO_TEMP_BEDROOM), end='')
        client.publish(topic=keys.AIO_TEMP_BEDROOM, msg=str(temperature))
        print("DONE")

        print("Publishing: {0} to {1} ... ".format(humidity, keys.AIO_HUM_BEDROOM), end='')
        client.publish(topic=keys.AIO_HUM_BEDROOM, msg=str(humidity))
        print("DONE")

    except Exception as error:
        print("Exception occurred", error)
    finally:
        last_random_sent_ticks = time.ticks_ms()

# Try WiFi Connection
try:
    ip = wifiConnection.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)

# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
client.subscribe(keys.AIO_LIGHTS_FEED)
print("Connected to %s, subscribed to %s topic" % (keys.AIO_SERVER, keys.AIO_LIGHTS_FEED))

# Code between try: and finally: may cause an error
# so ensure the client disconnects the server if
# that happens.
# Repeat this loop forever
# Action a message if one is received. Non-blocking.
# Send a random number to Adafruit IO if it's time.
# If an exception is thrown ...
# ... disconnect the client and clean up.

try:                      
    while 1:              
        client.check_msg()
        measure_temp_hum()
finally:                  
    client.disconnect()
    client = None
    wifiConnection.disconnect()
    print("Disconnected from Adafruit IO.")