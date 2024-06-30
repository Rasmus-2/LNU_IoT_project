import ubinascii              # Conversions between binary data and various encodings
import machine                # To Generate a unique id from processor

# Wireless network
WIFI_SSID =  "YOUR WIFI"
WIFI_PASS = "YOUR WIFI PASSWORD"

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "YOUR USERNAME AT ADAFRUIT"
AIO_KEY = "YOUR KEY GENERATED AT ADAFRUIT"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_LIGHTS_FEED = "YOUR_USERNAME/feeds/lights-bedroom"
AIO_TEMP_BEDROOM = "YOUR_USERNAME/feeds/temperature-bedroom"
AIO_HUM_BEDROOM = "YOUR_USERNAME/feeds/humidity-bedroom"