import asyncio
import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BOARD)

trig = 16
echo = 18
redled = 8
greenled = 10
blueled = 12

GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(redled, GPIO.OUT)
GPIO.setup(greenled, GPIO.OUT)
GPIO.setup(blueled, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

servo = GPIO.PWM(22,50)

BROKER = "broker.hivemq.com"  # Public MQTT broker
PORT = 1883
TOPIC_SEND = "parking/status"
TOPIC_RECEIVE = "parking/commands"

current_status = None  # None: unknown, 0: occupied, 1: free, 2: reserved

# Coordinates for the parking spot
LATITUDE = 45.1234
LONGITUDE = 25.1234

# Callback for receiving commands from MQTT
def on_message(client, userdata, message):
    global current_status
    try:
        command = json.loads(message.payload.decode())
        print(f"Received command: {command}")
        
        if command.get("spot_id") == 1:  # Only process commands for this spot
            new_status = command.get("status")

            # Process status 2 (reserved)
            if new_status == 2 and current_status == 1:
                GPIO.output(redled, GPIO.LOW)  # Blue color: Blue LED
                GPIO.output(greenled, GPIO.LOW)
                GPIO.output(blueled, GPIO.HIGH)
                print("Spot reserved.")
                current_status = new_status
                servo.start(0)
                servo.ChangeDutyCycle(2)

                # Send updated status
                send_parking_data(client, 1, current_status)

            # Process status 3 (resume sensor-based detection)
            elif new_status == 3 and current_status == 2:
                print("Resuming sensor-based detection.")
                current_status = None  # Reset to allow sensor to control
                servo.start(0)
                servo.ChangeDutyCycle(6)

                # Send updated status
                send_parking_data(client, 1, current_status)

            else:
                print("Spot is already taken")
                current_status = None
    except Exception as e:
        print(f"Error processing command: {e}")


# Function to calculate distance using ultrasonic sensor
def calculate_distance():
    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.00001)  # Trigger pulse for 10 microseconds
    GPIO.output(trig, GPIO.LOW)

    start = time.time()
    stop = time.time()

    # Wait for echo to start
    while GPIO.input(echo) == 0:
        start = time.time()

    # Wait for echo to end
    while GPIO.input(echo) == 1:
        stop = time.time()

    # Calculate distance based on duration
    duration = stop - start
    distance = (34300 / 2) * duration
    return distance

# Function to send parking data
def send_parking_data(client, spot_id, status):
    timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds
    payload = {
        "spot_id": spot_id,
        "status": status,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "timestamp": timestamp
    }
    client.publish(TOPIC_SEND, json.dumps(payload))
    print(f"Published status: {payload}")

# Main logic
async def main():
    global current_status

    client = mqtt.Client()
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC_RECEIVE)

    client.loop_start()
    
    spot_id = 1
    print("Monitoring parking spot...")

    try:
        while True:
            # Ignore sensor if spot is reserved (status 2)
            if current_status == 2:
                time.sleep(1)
                continue

            distance = calculate_distance()
            print(f"Measured Distance: {distance:.2f} cm")

            # Determine status based on distance
            new_status = 1 if distance >= 10 else 0

            # Send data only if status has changed
            if new_status != current_status:
                current_status = new_status
                send_parking_data(client, spot_id, current_status)

                if new_status == 1:  # Free
                    GPIO.output(greenled, GPIO.HIGH)
                    GPIO.output(redled, GPIO.LOW)
                    GPIO.output(blueled, GPIO.LOW)
                elif new_status == 0:  # Occupied
                    GPIO.output(redled, GPIO.HIGH)
                    GPIO.output(greenled, GPIO.LOW)
                    GPIO.output(blueled, GPIO.LOW)

            time.sleep(1)  # Small delay to avoid rapid re-triggering
    except KeyboardInterrupt:
        print("Exiting monitoring...")
    finally:
        GPIO.cleanup()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
