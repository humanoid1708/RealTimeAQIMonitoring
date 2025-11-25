import json
from kafka import KafkaConsumer
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
from collections import deque
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates

KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'realaq'
TOP_N_CITIES = 10 

latest_station_data = {}
fetch_timestamps = deque(maxlen=50)

fig, axes = plt.subplots(2, 2, figsize=(18, 10))

def get_aqi_bar_color(aqi_value):
    """Returns a color based on the AQI value for the bar chart."""
    if aqi_value is None or pd.isna(aqi_value): return 'gray'
    if aqi_value <= 50: return '#6AA84F' # Green
    if aqi_value <= 100: return '#F1C232' # Yellow
    if aqi_value <= 150: return '#F6B26B' # Orange
    if aqi_value <= 200: return '#E06666' # Red
    return '#A64D79' # Purple

def animate(i):
    """
    This function is called periodically to consume data from Kafka and update all plots.
    """
    messages = consumer.poll(timeout_ms=100, max_records=100)
    
    new_data_received = False
    for tp, msg_list in messages.items():
        for msg in msg_list:
            new_data_received = True
            data = msg.value
            station_name = data.get('station_name')
            if station_name:
                latest_station_data[station_name] = data

    if new_data_received:
        fetch_timestamps.append(datetime.now())

    if not latest_station_data:
        return 

    df = pd.DataFrame.from_dict(latest_station_data, orient='index')
    df = df.dropna(subset=['aqi']) 

    ax1 = axes[0, 0]
    ax1.clear()
    top_aqi_cities = df.sort_values(by='aqi', ascending=False).head(TOP_N_CITIES).iloc[::-1]
    
    colors = [get_aqi_bar_color(value) for value in top_aqi_cities['aqi']]
    ax1.barh(top_aqi_cities.index, top_aqi_cities['aqi'], color=colors, edgecolor='black')
    ax1.set_title(f'Top {TOP_N_CITIES} Cities by AQI', fontsize=14)
    ax1.set_xlabel('AQI Value')
    for index, value in enumerate(top_aqi_cities['aqi']):
        ax1.text(value + 1, index, str(int(value)), va='center')

    ax2 = axes[0, 1]
    ax2.clear()
    pm_data = df.loc[top_aqi_cities.index].iloc[::-1]
    
    y = np.arange(len(pm_data.index))
    height = 0.4
    ax2.barh(y + height/2, pm_data['pm10'], height, label='PM10', color='#A4C2F4', edgecolor='black')
    ax2.barh(y - height/2, pm_data['pm25'], height, label='PM2.5', color='#E06666', edgecolor='black')

    ax2.set_yticks(y, pm_data.index)
    ax2.set_title('PM10 vs PM2.5 Levels in Top AQI Cities', fontsize=14)
    ax2.set_xlabel('Concentration (µg/m³)')
    ax2.legend()

    ax3 = axes[1, 0]
    ax3.clear()
    top_co_cities = df.dropna(subset=['co']).sort_values(by='co', ascending=False).head(TOP_N_CITIES).iloc[::-1]
    
    ax3.barh(top_co_cities.index, top_co_cities['co'], color='#F6B26B', edgecolor='black')
    ax3.set_title(f'Top {TOP_N_CITIES} Cities by Carbon Monoxide (CO)', fontsize=14)
    ax3.set_xlabel('CO Level (ppm)')
    for index, value in enumerate(top_co_cities['co']):
        ax3.text(value, index, f'{value:.2f}', va='center')
        
    ax4 = axes[1, 1]
    ax4.clear()

    if fetch_timestamps:
        timestamps = list(fetch_timestamps)
        update_counts = range(len(timestamps))
        
        ax4.plot(timestamps, update_counts, marker='o', linestyle='-', color='#674EA7')

        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate(rotation=30)
        
    ax4.set_title('Data Fetch Timeline', fontsize=14)
    ax4.set_ylabel('Update Count')
    ax4.set_xlabel('Time of Fetch')
    ax4.grid(True, linestyle='--', alpha=0.6)


    fig.suptitle('Real-Time Air Quality Dashboard', fontsize=20, weight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

if __name__ == "__main__":
    print("Connecting to Kafka...")
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest'
    )
    print("Successfully connected. Starting visualization...")
    
    ani = FuncAnimation(fig, animate, interval=10000)
    
    plt.show()

