import asyncio
import aiocoap
import cbor
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BOARD)
SERVER_URL = "coap://13.53.114.140:3002/parking-status" 

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

# Helper function to send parking data
async def send_parking_data(spot_id, latitude, longitude, status):
    timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds

    payload = {
        "timestamp": timestamp,
        "parking_status": [
            {
                "id": 1,
                "lat": latitude,
                "lon": longitude,
                "s": status, 
            }
        ]
    }
    encoded_payload = cbor.dumps(payload)

    # Initialize CoAP context
    context = await aiocoap.Context.create_client_context()
    if context is None:
        print("Failed to initialize CoAP context")
        return

    try:
        request = aiocoap.Message(code=aiocoap.POST, uri=SERVER_URL, payload=encoded_payload)
        response = await context.request(request).response
        print(f"Response Code: {response.code}\nResponse Payload: {response.payload.decode()}")
    except Exception as e:
        print(f"Failed to send data: {e}")

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

# Main logic
async def main():
    spot_id = "spot_1"
    latitude = 45.1234
    longitude = 25.1234

    current_status = None  # None: unknown, 0: occupied, 1: free

    print("Monitoring parking spot...")

    while True:
        try:
            # Measure distance
            distance = calculate_distance()
            print(f"Measured Distance: {distance:.2f} cm")

            # Determine status based on distance
            if distance < 10:
                new_status = 0  # Occupied
                GPIO.output(greenled, GPIO.LOW)
                GPIO.output(redled, GPIO.HIGH)
            else:
                new_status = 1  # Free
                GPIO.output(redled, GPIO.LOW)
                GPIO.output(greenled, GPIO.HIGH)

            # Send data only if status has changed
            if new_status != current_status:
                current_status = new_status
                await send_parking_data(spot_id, latitude, longitude, current_status)
                print(f"Status updated and sent: {'Free' if current_status == 1 else 'Occupied'}")

            time.sleep(1)  # Small delay to avoid rapid re-triggering
        except KeyboardInterrupt:
            print("Exiting monitoring...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        GPIO.cleanup()
