import requests
import time
from datetime import datetime
import ssl
import json
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

API_KEY = "b36d6b364c9bb0a377f458fc2c623aa2a08da24e25bf9baa6be6270e4862e296" 

KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'realaq'

STATIONS = [
    # Maharashtra
    "Pune, Maharashtra", "Kothrud, Pune", "Hadapsar, Pune", "Katraj, Pune", "Bhosari, Pune", "Manjri, Pune",
    "Mumbai, Maharashtra", "Andheri, Mumbai", "Dadar, Mumbai", "Navi Mumbai",
    "Nagpur, Maharashtra", "Nashik, Maharashtra",
    # Delhi NCR
    "Delhi, India", "Connaught Place, Delhi", "Chandni Chowk, Delhi",
    "Noida, Uttar Pradesh", "Gurgaon, Haryana",
    # Karnataka
    "Bengaluru, Karnataka", "Koramangala, Bangalore", "Indiranagar, Bangalore", "Whitefield, Bangalore",
    "Mysuru, Karnataka", "Mangaluru, Karnataka",
    # Tamil Nadu
    "Chennai, Tamil Nadu", "T. Nagar, Chennai", "Adyar, Chennai",
    "Coimbatore, Tamil Nadu", "Madurai, Tamil Nadu",
    # Telangana
    "Hyderabad, Telangana", "Gachibowli, Hyderabad", "Banjara Hills, Hyderabad",
    # West Bengal
    "Kolkata, West Bengal", "Salt Lake, Kolkata", "Howrah, West Bengal",
    # Gujarat
    "Ahmedabad, Gujarat", "Surat, Gujarat", "Vadodara, Gujarat",
    # Rajasthan
    "Jaipur, Rajasthan", "Jodhpur, Rajasthan", "Udaipur, Rajasthan",
    # Uttar Pradesh
    "Lucknow, Uttar Pradesh", "Kanpur, Uttar Pradesh", "Varanasi, Uttar Pradesh",
    # Madhya Pradesh
    "Bhopal, Madhya Pradesh", "Indore, Madhya Pradesh",
    # Other Major Cities
    "Patna, Bihar", "Visakhapatnam, Andhra Pradesh", "Chandigarh", "Bhubaneswar, Odisha", "Kochi, Kerala"
]

FETCH_INTERVAL_SECONDS = 5 

def force_tls_v12():
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl._create_default_https_context = lambda: context
        print("Applied workaround: Forcing TLSv1.2 protocol.")
    except Exception as e:
        print(f"Warning: Could not force TLSv1.2. Details: {e}")

def get_aqi_data(city_name, api_key):
    url = f"https://api.ambeedata.com/latest/by-city"
    params = {"city": city_name}
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        data = response.json()
        if data.get("message") == "success" and data.get("stations"):
            return data["stations"][0]
        else:
            print(f"API returned an error or no data for '{city_name}': {data.get('message')}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for '{city_name}': {e}")
    return None

def process_data(raw_data, requested_city):
    if not raw_data:
        return None
    return {
        "station_name": requested_city,
        "latitude": raw_data.get('lat'),
        "longitude": raw_data.get('lng'),
        "aqi": raw_data.get('AQI'),
        "pm25": raw_data.get('PM25'),
        "o3": raw_data.get('OZONE'),
        "no2": raw_data.get('NO2'),
        "co": raw_data.get('CO'),
        "pm10": raw_data.get('PM10'),
        "so2": raw_data.get('SO2'),
        "timestamp": datetime.now().isoformat()
    }

def create_kafka_producer():
    """Creates and returns a Kafka producer."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Successfully connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
        return producer
    except NoBrokersAvailable:
        print(f"Error: Could not connect to Kafka broker at {KAFKA_BOOTSTRAP_SERVERS}.")
        print("Please ensure Kafka is running and the address is correct.")
        return None

def main():
    """Main loop to fetch data and send it to Kafka."""
    force_tls_v12()
    
    producer = create_kafka_producer()
    if not producer:
        return

    print(f"\nStarting Big Data AQI Producer for {len(STATIONS)} locations...")
    print(f"Streaming data to Kafka topic: '{KAFKA_TOPIC}'")
    print("Press Ctrl+C to stop.")

    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    while True:
        try:
            records_sent = 0
            for city in STATIONS:
                raw_data = get_aqi_data(city, API_KEY)
                processed = process_data(raw_data, city)
                if processed:
                    
                    producer.send(KAFKA_TOPIC, value=processed)
                    records_sent += 1
            
            producer.flush()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent {records_sent} records to Kafka topic '{KAFKA_TOPIC}'.")

            time.sleep(FETCH_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\nStopping the script. Goodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            time.sleep(FETCH_INTERVAL_SECONDS)
    
    producer.close()

if __name__ == "__main__":
    if "YOUR_API_KEY" in API_KEY:
        print("ERROR: Please replace with your actual Ambee API key.")
    else:
        main()

