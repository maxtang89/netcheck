import socket
import time
import datetime
import subprocess
import speedtest
import locale
import os
import dns.resolver
import yaml
import ipaddress
import threading
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import shutil

CONFIG_PATH = "./config.yaml"

# System encoding detection
decode_type = locale.getpreferredencoding()

# Global variables for iPerf process management
iperf_process = None
iperf_timer = None

def load_config():
    """Load configuration from YAML file."""
    try:
        with open(CONFIG_PATH, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Failed to load config: {e}")
        return {}

config = load_config()
API_KEY = config.get("api_key", "")
ALLOWED_IPS = config.get("allowed_ips", [])

# System hostname
HOST_NAME = socket.gethostname()

# Determine OS type
user_os = "unknown"
if os.name == "nt":
    user_os = "windows"
elif os.name == "posix":
    user_os = "linux"
else:
    print("Unsupported OS detected. Exiting...")
    exit(1)

def is_ip_allowed(client_ip):
    """Check if the client's IP is within the allowed range."""
    if not ALLOWED_IPS:
        return True  # If no restriction is set, allow all.
    try:
        client_ip_obj = ipaddress.ip_address(client_ip)
        return any(
            client_ip_obj in ipaddress.ip_network(cidr, strict=False)
            for cidr in ALLOWED_IPS
        )
    except ValueError:
        return False

def ping(host, count=3, warmup=0, timeout=3):
    """Perform ICMP or TCP ping test with warmup and multiple counts, ensuring a 1-second interval."""
    if not host:
        return None

    method = "tcp"
    if ":" in host:
        host, port = host.split(":")
        port = int(port)
    else:
        method = "icmp"

    results = []

    # Perform warm-up pings
    for _ in range(warmup):
        _ = ping(host, count=1, timeout=timeout)
        time.sleep(1)  # Ensure 1-second interval between warm-up pings

    # Perform actual pings
    for _ in range(count):
        try:
            if method == "tcp":
                start_time = time.time()
                with socket.create_connection((host, port), timeout):
                    end_time = time.time()
                results.append(round((end_time - start_time) * 1000, 2))
            else:
                start_time = time.time()
                command = ["ping", "-n", "1", host] if user_os == "windows" else ["ping", "-c", "1", host]
                try:
                    output = subprocess.check_output(command, timeout=timeout, stderr=subprocess.DEVNULL).decode(decode_type)
                    if "Unknown" in output or "Unreachable" in output or "not known" in output:
                        results.append(-1)
                        break
                    else:
                        end_time = time.time()
                        results.append(round((end_time - start_time) * 1000, 2))
                except subprocess.CalledProcessError:
                    results.append(-1)
        except (subprocess.TimeoutExpired, socket.timeout, ConnectionRefusedError):
            results.append(-1)
        time.sleep(1)  # Ensure 1-second interval between actual pings

    # Compute statistics
    valid_results = [r for r in results if r != -1]
    total = len(results)
    lost = total - len(valid_results)
    

    if len(valid_results) == 0:
        min_result = -1
        max_result = -1
        avg_result = -1
        loss_rate = 100
    else:
        min_result = min(valid_results)
        max_result = max(valid_results)
        avg_result = sum(valid_results) / len(valid_results)
        loss_rate = int((lost / total) * 100 if total > 0 else 0)

    min_result = int(min_result)
    max_result = int(max_result)
    avg_result = int(avg_result)

    return {
        "host": host,
        "protocol": method,
        "count": count,
        "warmup": warmup,
        "timeout": timeout,
        "min": min_result,
        "max": max_result,
        "avg": avg_result,
        "loss": loss_rate,
        "raw": results,
        "brackets": [min_result, avg_result, max_result, loss_rate]
    }

def speed():
    """Perform a Speedtest to measure download and upload speeds."""
    servers = []
    try:
        spd = speedtest.Speedtest(secure=True)
        spd.get_best_server()
        download_speed = int((spd.download() / 1_000_000))
        upload_speed = int((spd.upload() / 1_000_000))
        ping = int(spd.results.ping)
        return {
            "download": download_speed,
            "upload": upload_speed,
            "ping": ping,
            "raw": spd.results.dict(),
            "brackets": [upload_speed, download_speed, ping]
        }
    except Exception as e:
        return {"error": str(e)}

def start_iperf_server(port=5201):
    """Start an iPerf server."""
    global iperf_process, iperf_timer
    if shutil.which("iperf3") is None:
        return {"message": "iperf3 is not installed on this system."}
    if iperf_process:
        return {"message": "iPerf server is already running"}
    try:
        iperf_process = subprocess.Popen(["iperf3", "-s", "-p", str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        iperf_timer = threading.Timer(600, stop_iperf_server)
        iperf_timer.start()
        return {"message": "iPerf server started", "port": port}
    except Exception as e:
        return {"message": str(e)}

def stop_iperf_server():
    """Stop the running iPerf server."""
    global iperf_process, iperf_timer
    if iperf_process:
        iperf_process.terminate()
        iperf_process = None
    if iperf_timer:
        iperf_timer.cancel()
        iperf_timer = None
    return {"message": "iPerf server stopped"}

def format_response(data, response_format="json"):
    """Convert JSON data to [][] format if requested."""
    if response_format == "brackets":
        if isinstance(data, dict) and "data" in data and "brackets" in data["data"]:
            return PlainTextResponse("[{}]".format("][".join(map(str, data["data"]["brackets"]))), media_type="text/plain")
    return data

# FastAPI app initialization
app = FastAPI()

@app.get("/")
def root():
    return {"message": "NetCheck API"}

@app.get("/ping")
def get_ping(request: Request, api_key : str = "", host: str = "www.google.com", count: int = 3, warmup: int = 0, timeout: int = 3, format: str = "json"):
    if not is_ip_allowed(request.client.host) or (API_KEY and api_key != API_KEY):
        return format_response({"error": "Forbidden"}, format)
    return format_response({"host": HOST_NAME, "data": ping(host, count, warmup, timeout)}, format)

@app.get("/iperf/start")
def start_iperf_api(request: Request, api_key : str = "", format: str = "json"):
    if not is_ip_allowed(request.client.host) or (API_KEY and api_key != API_KEY):
        return format_response({"error": "Forbidden"}, format)
    return format_response(start_iperf_server(), format)

@app.get("/iperf/stop")
def stop_iperf_api(request: Request, api_key : str = "", format: str = "json"):
    if not is_ip_allowed(request.client.host) or (API_KEY and api_key != API_KEY):
        return format_response({"error": "Forbidden"}, format)
    return format_response(stop_iperf_server(), format)

@app.get("/healthy")
def health_check(format: str = "json"):
    return format_response({
        "status": "healthy",
        "host": HOST_NAME,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, format)

@app.get("/speed")
def get_speed(format: str = "json", api_key : str = "", request: Request = None):
    if not is_ip_allowed(request.client.host) or (API_KEY and api_key != API_KEY):
        return format_response({"error": "Forbidden"}, format)
    return format_response({"host": HOST_NAME, "data": speed()}, format)

def traceroute(target):
    """Perform a network traceroute to a given target."""
    try:
        command = ["tracert", "-d", target] if user_os == "windows" else ["traceroute", "-n", target]
        output = subprocess.check_output(command, timeout=10).decode(decode_type)
        output = output.splitlines()
        return {"result": output}
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}
    except subprocess.TimeoutExpired:
        return {"error": "Traceroute timed out"}

@app.get("/traceroute")
def get_traceroute(target: str, api_key : str = "", format: str = "json", request: Request = None):
    if not is_ip_allowed(request.client.host) or (API_KEY and api_key != API_KEY):
        return format_response({"error": "Forbidden"}, format)
    return format_response({"host": HOST_NAME, "data": traceroute(target)}, format)

def dns_lookup(domain):
    """Perform a DNS lookup for the given domain."""
    try:
        resolver = dns.resolver.Resolver()
        answers = resolver.resolve(domain, "A")
        return {"domain": domain, "records": [r.address for r in answers]}
    except dns.resolver.NXDOMAIN:
        return {"error": "Domain does not exist"}
    except dns.resolver.Timeout:
        return {"error": "DNS query timed out"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/dns")
def get_dns(domain: str, api_key : str = "", format: str = "json", request: Request = None):
    if not is_ip_allowed(request.client.host) or (API_KEY and api_key != API_KEY):
        return format_response({"error": "Forbidden"}, format)
    return format_response({"host": HOST_NAME, "data": dns_lookup(domain)}, format)
