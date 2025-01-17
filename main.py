import asyncio
import aiocoap
import cbor

# URL-ul serverului CoAP (înlocuiește <SERVER_IP> cu adresa serverului)
SERVER_URL = "coap://<SERVER_IP>:3002/parking-status"

# Funcție pentru a trimite date pentru un singur loc de parcare
async def send_parking_data(spot_id, latitude, longitude, status):
    # Generează un timestamp curent
    timestamp = int(time.time() * 1000)  # Timpul în milisecunde
    
    # Pregătește payload-ul
    payload = {
        "timestamp": timestamp,
        "parking_status": [
            {
                "id": spot_id,
                "lat": latitude,
                "lon": longitude,
                "s": status,  # 1 = liber, 0 = ocupat
            }
        ]
    }
    encoded_payload = cbor.dumps(payload)

    # Trimite payload-ul către server
    context = await aiocoap.Context.create_client_context()
    try:
        request = aiocoap.Message(code=aiocoap.POST, uri=SERVER_URL, payload=encoded_payload)
        response = await context.request(request).response
        print(f"Response Code: {response.code}\nResponse Payload: {response.payload.decode()}")
    except Exception as e:
        print(f"Failed to send data: {e}")

# Bucla principală pentru a trimite datele bazate pe inputul utilizatorului
async def main():
    spot_id = "spot_1"  # ID-ul locului de parcare
    latitude = 45.1234  # Latitudine exemplu
    longitude = 25.1234  # Longitudine exemplu
    
    print("Tastează '1' pentru liber, '0' pentru ocupat sau 'q' pentru a ieși.")
    
    while True:
        user_input = input("Introduceți statusul locului de parcare (1/0): ").strip()
        
        if user_input == "1":
            await send_parking_data(spot_id, latitude, longitude, 1)
            print(f"Statusul pentru {spot_id} a fost trimis ca 'liber'.")
        elif user_input == "0":
            await send_parking_data(spot_id, latitude, longitude, 0)
            print(f"Statusul pentru {spot_id} a fost trimis ca 'ocupat'.")
        elif user_input.lower() == "q":
            print("Ieșire din program.")
            break
        else:
            print("Input invalid. Tastează '1', '0' sau 'q'.")

if __name__ == "__main__":
    asyncio.run(main())
