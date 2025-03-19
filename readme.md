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
```bash
sudo apt install traceroute -y && sudo apt install iperf3 -y
```
### Steps
1. Clone the repository:
    ```sh
    git clone https://github.com/maxtang89/netcheck.git
    cd netcheck
    ```
2. Edit the configuration:
     ```sh
    vi config.yaml
    ```
3. Run the installation script:
    ```sh
    sudo chmod 775 ./install.sh
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
    "host": "xxx",
    "data": {
        "host": "google.com",
        "protocol": "icmp",
        "count": 5,
        "warmup": 0,
        "timeout": 2,
        "min": 8,
        "max": 48,
        "avg": 16,
        "loss": 0,
        "raw": [48.67, 9.05, 9.03, 8.78, 9.3],
        "brackets": [8, 16, 48, 0]
    }
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
    "host": "xxx",
    "data": {
        "download": 1635,
        "upload": 1682,
        "brackets": [
            1682,
            1635
        ]
    }
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
    "host": "xxx",
    "data": {
        "result": [
            "traceroute to 8.8.8.8 (8.8.8.8), 30 hops max, 60 byte packets",
            " 1  xxx.xxx.xxx.xxx  0.773 ms  0.813 ms  0.835 ms",
            " 2  xxx.xxx.xxx.xxx  1.384 ms  1.525 ms  1.632 ms",
            " 3  xxx.xxx.xxx.xxx  1.241 ms  1.448 ms  1.397 ms",
            " 4  xxx.xxx.xxx.xxx  2.440 ms  2.494 ms  2.419 ms",
            " 5  xxx.xxx.xxx.xxx  3.412 ms  3.918 ms  3.399 ms",
            " 6  xxx.xxx.xxx.xxx  3.292 ms  3.138 ms  3.153 ms",
            " 7  xxx.xxx.xxx.xxx  3.695 ms  3.778 ms  3.786 ms",
            " 8  * * *",
            " 9  8.8.8.8  3.630 ms  3.564 ms  3.550 ms"
        ]
    }
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
    "host": "xxx",
    "data": {
        "domain": "google.com",
        "records": [
            "142.250.66.78"
        ]
    }
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