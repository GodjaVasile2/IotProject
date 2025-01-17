import asyncio
import aiocoap
import cbor
import time

# Replace <SERVER_IP> with the actual IP address of your CoAP server
SERVER_URL = "coap://127.0.0.1:3002/parking-status"  # Update with your server's IP and port

async def send_parking_data(spot_id, latitude, longitude, status):
    timestamp = int(time.time() * 1000)  # Current time in milliseconds

    # Prepare the payload
    payload = {
        "timestamp": timestamp,
        "parking_status": [
            {
                "id": spot_id,
                "lat": latitude,
                "lon": longitude,
                "s": status,  # 1 = free, 0 = occupied
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

async def main():
    spot_id = "spot_1"
    latitude = 45.1234
    longitude = 25.1234

    print("Type '1' for free, '0' for occupied, or 'q' to quit.")

    while True:
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
