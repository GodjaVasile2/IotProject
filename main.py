import asyncio
import aiocoap
import cbor
import time

# Replace <SERVER_IP> with the IP of the EC2 instance
SERVER_URL = "coap://<SERVER_IP>:3002/parking-status"

async def send_parking_data(spot_id, latitude, longitude, status):
    # Prepare the payload
    payload = {
        "spot_id": spot_id,
        "latitude": latitude,
        "longitude": longitude,
        "status": status,  # 'free' or 'occupied'
        "timestamp": int(time.time() * 1000),  # Current timestamp in milliseconds
    }
    encoded_payload = cbor.dumps(payload)

    # Create CoAP client context
    context = await aiocoap.Context.create_client_context()

    # Create CoAP POST request
    request = aiocoap.Message(code=aiocoap.POST, uri=SERVER_URL, payload=encoded_payload)

    try:
        # Send the request and await the response
        response = await context.request(request).response
        print(f"Response Code: {response.code}")
        print(f"Response Payload: {response.payload.decode()}")
    except Exception as e:
        print(f"Failed to send data: {e}")

async def main():
    spot_id = "spot_1"
    latitude = 45.1234
    longitude = 25.1234

    print("Type '1' for free, '0' for occupied, or 'q' to quit.")
    while True:
        user_input = input("Enter parking spot status (1/0): ").strip()
        if user_input == "1":
            await send_parking_data(spot_id, latitude, longitude, "free")
        elif user_input == "0":
            await send_parking_data(spot_id, latitude, longitude, "occupied")
        elif user_input.lower() == "q":
            print("Exiting.")
            break
        else:
            print("Invalid input. Try again.")

if __name__ == "__main__":
    asyncio.run(main())
