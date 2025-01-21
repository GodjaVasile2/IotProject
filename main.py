#import the libraries used
import asyncio
import aiocoap
import cbor
import RPi.GPIO as GPIO
import time

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

async def send_parking_data(spot_id, latitude, longitude, status):
    timestamp = int(time.time() * 1000)  

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

def calculate_distance():
 #set the trigger to HIGH
    GPIO.output(trig, GPIO.HIGH)
 #sleep 0.00001 s and the set the trigger to LOW
    time.sleep(1)
    GPIO.output(trig, GPIO.LOW)
 #save the start and stop times
    start = time.time()
    stop = time.time()
 #modify the start time to be the last time until
 #the echo becomes HIGH
    while GPIO.input(echo) == 0:
        start = time.time()
 #modify the stop time to be the last time until
 #the echo becomes LOW
    while GPIO.input(echo) == 1:
        stop = time.time()
#get the duration of the echo pin as HIGH
    duration = stop - start
 #calculate the distance
    distance = 34300/2 * duration
    print(distance)
    return distance

GPIO.output(redled, GPIO.LOW)
GPIO.output(greenled, GPIO.HIGH)


async def main():
    spot_id = "spot_1"
    latitude = 45.1234
    longitude = 25.1234

    print("Type '1' for free, '0' for occupied, or 'q' to quit.")
    
    while True:
        
        if calculate_distance() < 10:
            GPIO.output(greenled, GPIO.LOW)
            GPIO.output(redled, GPIO.HIGH)
        else:
            GPIO.output(redled, GPIO.LOW)
            GPIO.output(greenled, GPIO.HIGH)
            
        user_input = input("Enter parking spot status (1/0): ").strip()

        if user_input == "1":
            await send_parking_data(spot_id, latitude, longitude, 1)
            print(f"Status for {spot_id} sent as 'free'.")
        elif user_input == "0":
            await send_parking_data(spot_id, latitude, longitude, 0)
            print(f"Status for {spot_id} sent as 'occupied'.")
        elif user_input.lower() == "q":
            print("Exiting program.")
            break
        else:
            print("Invalid input. Type '1', '0', or 'q'.")

if __name__ == "__main__":
    asyncio.run(main())

GPIO.cleanup()


