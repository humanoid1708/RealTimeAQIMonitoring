# Real-Time Air Quality Monitoring System

A Big Data Technology project that utilizes **Apache Kafka** for streaming analytics to monitor, process, and visualize Air Quality Index (AQI) data in real-time.

## 📖 Project Overview

Air pollution is a critical global issue requiring constant monitoring. This project implements a **Real-Time Data Pipeline** that:

1. **Ingests Data:** Fetches live AQI data for major Indian cities using the Ambee API.
2. **Streams Data:** Uses Apache Kafka (Producer) to stream pollutant data (PM2.5, PM10, CO, NO2, etc.).
3. **Processes & Visualizes:** Consumes the stream and renders a live, dynamic dashboard using Matplotlib.

### Key Features

- **Live Analytics:** Updates AQI data every few seconds.
- **Dynamic Dashboard:** Visualizes Top 10 Cities by AQI, PM10 vs PM2.5 comparisons, CO levels, and data fetch latency.
- **Scalability:** Built on Apache Kafka to handle high-throughput message streams.

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Streaming Platform:** Apache Kafka (with Zookeeper)
- **Visualization:** Matplotlib, Pandas
- **Data Source:** Ambee Air Quality API

## ⚙️ Prerequisites & Installation

### 1. Install System Dependencies

- **Java (JDK 8+):** Required to run Apache Kafka and Zookeeper.
- **Apache Kafka:** [Download Kafka](https://kafka.apache.org/downloads) and extract it to a folder (e.g., `C:\kafka`).

### 2. Install Python Libraries

Install the required Python packages using pip:

```
pip install kafka-python requests matplotlib pandas numpy

```

*(Note: If you encounter issues with `kafka-python`, you may try `pip install kafka-python-ng`)*

### 3. API Configuration

The project uses the **Ambee API**.

1. Open `aqi_fetcher.py`.
2. Ensure the `API_KEY` variable is set.

## 🚀 How to Run the Pipeline

To run this project, you need to open **4 separate terminal windows** (Command Prompt or PowerShell). Follow the order below strictly.

**Note:** The commands below assume you are inside your Kafka installation directory (e.g., `C:\kafka`).

### Step 1: Start Zookeeper (Terminal 1)

Zookeeper manages the Kafka cluster state.

```
bin\windows\zookeeper-server-start.bat config\zookeeper.properties

```

*Wait until you see "binding to port..." messages.*

### Step 2: Start Kafka Broker (Terminal 2)

The broker handles the message storage and transfer.

```
bin\windows\kafka-server-start.bat config\server.properties

```

*Wait until you see "started (kafka.server.KafkaServer)" messages.*

### Step 3: Create the Kafka Topic (Terminal 2 or new)

Create the specific topic used by the python scripts (`realaq`).

```
bin\windows\kafka-topics.bat --create --topic realaq --bootstrap-server localhost:9092

```

### Step 4: Start the Producer (Terminal 3)

This script fetches data from the API and pushes it to the Kafka topic.

```
python aqi_fetcher.py

```

*You should see output like: `Sent X records to Kafka topic 'realaq'`.*

### Step 5: Start the Visualization Consumer (Terminal 4)

This script reads from Kafka and launches the dashboard.

```
python visualization.py

```

*A Matplotlib window will open, displaying real-time charts updating every few seconds.*

## 📊 Dashboard Insights

The visualization window displays four real-time charts:

1. **Top 10 Cities by AQI:** Bar chart showing the most polluted cities currently.
2. **PM10 vs PM2.5:** Comparative analysis of particulate matter.
3. **CO Levels:** Tracks Carbon Monoxide levels in major cities.
4. **Data Fetch Timeline:** Monitors the health of the data stream and update frequency.

## 📂 Project Structure

- `aqi_fetcher.py`: **(Producer)** Connects to Ambee API and sends JSON data to Kafka.
- `visualization.py`: **(Consumer)** Reads JSON data from Kafka and animates the graphs.
