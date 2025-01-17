import requests

# URL-ul serverului HTTP (înlocuiește <SERVER_IP> cu adresa serverului)
SERVER_URL = "http://<SERVER_IP>:3001/parking-status"

def send_parking_data(spot_id, latitude, longitude, status):
    # Exemplu de date
    payload = {
        "spot_id": spot_id,
        "latitude": latitude,
        "longitude": longitude,
        "status": status  # "free" sau "occupied"
    }

    try:
        # Trimite cererea POST
        response = requests.post(SERVER_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Failed to send data: {e}")

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
