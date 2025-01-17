from coapthon.client.helperclient import HelperClient

# Replace <SERVER_IP> with the public IP or hostname of your CoAP server
SERVER_IP = "<SERVER_IP>"
SERVER_PORT = 3002  # CoAP server port
RESOURCE_PATH = "parking-status"  # CoAP resource path

def send_parking_data(spot_id, latitude, longitude, status):
    # Initialize CoAP client
    client = HelperClient(server=(SERVER_IP, SERVER_PORT))

    # Create payload
    payload = f"""
    {{
        "spot_id": "{spot_id}",
        "latitude": {latitude},
        "longitude": {longitude},
        "status": "{status}"
    }}
    """

    try:
        # Send a POST request
        response = client.post(RESOURCE_PATH, payload)
        if response:
            print(f"Response Code: {response.code}")
            print(f"Response Payload: {response.payload}")
        else:
            print("No response received from server.")
    except Exception as e:
        print(f"Failed to send data: {e}")
    finally:
        # Stop the client
        client.stop()

if __name__ == "__main__":
    spot_id = "spot_1"
    latitude = 45.1234
    longitude = 25.1234

    print("Type '1' for free, '0' for occupied, or 'q' to quit.")
    while True:
        user_input = input("Enter parking spot status (1/0): ").strip()
        if user_input == "1":
            send_parking_data(spot_id, latitude, longitude, "free")
        elif user_input == "0":
            send_parking_data(spot_id, latitude, longitude, "occupied")
        elif user_input.lower() == "q":
            print("Exiting.")
            break
        else:
            print("Invalid input. Try again.")
