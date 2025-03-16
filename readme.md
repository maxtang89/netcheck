# NetCheck

NetCheck is a lightweight network diagnostic tool that provides an API for checking network quality. It includes functionalities such as ICMP/TCP ping, Speedtest, traceroute, DNS lookup, and iPerf3 bandwidth measurement.

## Features
- **Ping (ICMP/TCP)**: Measure network latency and packet loss.
- **Speedtest**: Check internet upload and download speed.
- **Traceroute**: Track the path packets take to reach a target.
- **DNS Lookup**: Resolve domain names to IP addresses.
- **iPerf3 Server**: Start an iPerf3 server for bandwidth testing.

## Installation

### Prerequisites
- Ubuntu/Debian-based system
- Python 3.10+
- `traceroute` and `iperf3` installed (for full functionality)

### Steps
1. Clone the repository:
    ```sh
    git clone https://github.com/maxtang89/netcheck.git
    cd netcheck
    ```
2. Run the installation script:
    ```sh
    sudo ./install.sh
    ```
    This script will:
    - Create a Python virtual environment.
    - Install required dependencies from `requirements.txt`.
    - Configure and start NetCheck as a systemd service.

## Configuration
NetCheck uses a YAML configuration file (`config.yaml`) for settings:
```yaml
api_key: "your_api_key"
port: 8080
allowed_ips:
  - "192.168.1.0/24"
  - "10.0.0.0/8"
```
- **`api_key`**: API key required for requests (optional).
- **`port`**: The port NetCheck runs on.
- **`allowed_ips`**: CIDR ranges of allowed client IPs.

## API Endpoints

### **1. Ping**
Perform ICMP or TCP ping to a target.

#### **Endpoint:**
```
GET /ping
```
#### **Parameters:**
| Parameter  | Type   | Required | Description |
|------------|--------|----------|------------|
| `host`     | string | ✅ Yes   | Target hostname or IP (e.g., `google.com`, `8.8.8.8`) |
| `count`    | int    | ❌ No   | Number of ping attempts (default: `3`) |
| `warmup`   | int    | ❌ No   | Number of warm-up pings before actual test (default: `0`) |
| `timeout`  | int    | ❌ No   | Timeout per ping attempt in seconds (default: `3`) |
| `api_key`  | string | ❌ No   | API key for authentication (if required) |
| `format`   | string | ❌ No   | Response format (`json` or `brackets`) |

#### **Example Request:**
```sh
curl "http://server-ip:8080/ping?host=google.com&count=5&timeout=2&format=json&api_key=your_api_key"
```

#### **Example Response:**
```json
{
  "host": "nac",
  "data": {
    "host": "google.com",
    "protocol": "icmp",
    "count": 5,
    "warmup": 0,
    "timeout": 2,
    "min": 9,
    "max": 9,
    "avg": 9,
    "loss": 20,
    "raw": [null, 9.46, 9.34, 9.33, 9.28],
    "brackets": [9, 9, 9, 20]
  },
}
```

---

### **2. Speedtest**
Measure internet speed.

#### **Endpoint:**
```
GET /speed
```
#### **Parameters:**
| Parameter  | Type   | Required | Description |
|------------|--------|----------|------------|
| `api_key`  | string | ❌ No   | API key for authentication (if required) |
| `format`   | string | ❌ No   | Response format (`json` or `brackets`) |

#### **Example Request:**
```sh
curl "http://server-ip:8080/speed?format=json&api_key=your_api_key"
```

#### **Example Response:**
```json
{
  "download": 95,
  "upload": 20
}
```

---

### **3. Traceroute**
Check the route to a target IP.

#### **Endpoint:**
```
GET /traceroute
```
#### **Parameters:**
| Parameter  | Type   | Required | Description |
|------------|--------|----------|------------|
| `target`   | string | ✅ Yes   | Target hostname or IP (e.g., `8.8.8.8`) |
| `api_key`  | string | ❌ No   | API key for authentication (if required) |
| `format`   | string | ❌ No   | Response format (`json` or `brackets`) |

#### **Example Request:**
```sh
curl "http://server-ip:8080/traceroute?target=8.8.8.8&format=json&api_key=your_api_key"
```

#### **Example Response:**
```json
{
  "result": [
    "raw traceout output (split by lines)"
  ]
}
```

---

### **4. DNS Lookup**
Resolve a domain to its IP address.

#### **Endpoint:**
```
GET /dns
```
#### **Parameters:**
| Parameter  | Type   | Required | Description |
|------------|--------|----------|------------|
| `domain`   | string | ✅ Yes   | Domain name to resolve (e.g., `google.com`) |
| `api_key`  | string | ❌ No   | API key for authentication (if required) |
| `format`   | string | ❌ No   | Response format (`json` or `brackets`) |

#### **Example Request:**
```sh
curl "http://server-ip:8080/dns?domain=google.com&format=json&api_key=your_api_key"
```

#### **Example Response:**
```json
{
  "domain": "google.com",
  "records": ["8.8.8.8", "8.8.4.4"]
}
```

---

### **5. iPerf3 Server**
Start or stop an iPerf3 server for bandwidth testing.

#### **Start iPerf3 Server**
```
GET /iperf/start
```
#### **Stop iPerf3 Server**
```
GET /iperf/stop
```
#### **Parameters:**
| Parameter  | Type   | Required | Description |
|------------|--------|----------|------------|
| `api_key`  | string | ❌ No   | API key for authentication (if required) |
| `format`   | string | ❌ No   | Response format (`json` or `brackets`) |

#### **Example Request (Start Server):**
```sh
curl "http://server-ip:8080/iperf/start?format=json&api_key=your_api_key"
```

#### **Example Response:**
```json
{
  "message": "iPerf server started",
  "port": 5201
}
```

#### **Example Request (Stop Server):**
```sh
curl "http://server-ip:8080/iperf/stop?format=json&api_key=your_api_key"
```

#### **Example Response:**
```json
{
  "message": "iPerf server stopped"
}
```

---

### **6. Health Check**
Check if the NetCheck service is running.

#### **Endpoint:**
```
GET /healthy
```
#### **Parameters:**
| Parameter  | Type   | Required | Description |
|------------|--------|----------|------------|
| `format`   | string | ❌ No   | Response format (`json` or `brackets`) |

#### **Example Request:**
```sh
curl "http://server-ip:8080/healthy?format=json"
```
#### **Example Response:**
```json
{
  "status": "healthy",
  "host": "netcheck-server",
  "time": "2025-03-16 14:00:00"
}
```

## Running & Managing NetCheck
NetCheck is installed as a systemd service:
```sh
sudo systemctl start netcheck
sudo systemctl stop netcheck
sudo systemctl restart netcheck
sudo systemctl status netcheck
```

## License
This project is licensed under the MIT License.