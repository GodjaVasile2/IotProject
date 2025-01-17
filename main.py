import asyncio
import aiocoap
import cbor

# Replace with the actual IP and port of your CoAP server
SERVER_URL = "coap://127.0.0.1:3002/parking-status"

async def send_parking_data():
    # Example data
    payload = {
        "spot_id": "spot_1",
        "latitude": 45.1234,
        "longitude": 25.1234,
        "status": "free"  # or "occupied"
    }
    encoded_payload = cbor.dumps(payload)

    # Create a CoAP client context
    context = await aiocoap.Context.create_client_context()

    # Create a CoAP POST request
    request = aiocoap.Message(code=aiocoap.POST, uri=SERVER_URL, payload=encoded_payload)

    try:
        # Send the request and await the response
        response = await context.request(request).response
        print(f"Response Code: {response.code}")
        print(f"Response Payload: {response.payload.decode()}")
    except Exception as e:
        print(f"Failed to send data: {e}")

if __name__ == "__main__":
    asyncio.run(send_parking_data())
