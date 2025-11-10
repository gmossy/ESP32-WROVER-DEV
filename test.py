#!/usr/bin/env python3
"""
ESP32S3 Webserver Connectivity Diagnostic Tool
Tests network connectivity to ESP32S3 at 10.0.0.30
Automatically detects ESP32 USB port
"""

import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
import re
import os
from datetime import datetime

ESP32_IP = "10.0.0.30"
HTTP_PORT = 80
TIMEOUT = 5
CAPTURE_DIR = "captures"

def find_esp32_port():
    """Find the USB port connected to ESP32 device"""
    try:
        result = subprocess.run(
            ["arduino-cli", "board", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Look for ESP32 Family Device or Serial Port (USB) in output
        lines = result.stdout.split('\n')
        esp32_port = None
        
        for line in lines:
            if "ESP32 Family Device" in line or "Serial Port (USB)" in line:
                # Extract port from the beginning of the line (handle full port names)
                port_match = re.match(r'^(/dev/cu\.\w+\d*)', line.strip())
                if not port_match:
                    # Try alternative pattern for different port formats
                    port_match = re.match(r'^(/dev/\w+\d*)', line.strip())
                if port_match:
                    esp32_port = port_match.group(1)
                    break
        
        if esp32_port:
            print(f"✓ ESP32 detected on port: {esp32_port}")
            return esp32_port
        else:
            print("✗ No ESP32 device found")
            print("Available ports:")
            for line in lines:
                if "/dev/" in line and line.strip():
                    print(f"  {line.strip()}")
            return None
            
    except Exception as e:
        print(f"✗ Error detecting ESP32 port: {e}")
        return None

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_ping():
    """Test ICMP ping connectivity"""
    print_section("1. ICMP Ping Test")
    try:
        result = subprocess.run(
            ["ping", "-c", "4", "-W", "1000", ESP32_IP],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(result.stdout)
        if result.returncode == 0:
            print("✓ Ping successful - Device is reachable at network layer")
            return True
        else:
            print("✗ Ping failed - Device not responding to ICMP")
            return False
    except Exception as e:
        print(f"✗ Ping test error: {e}")
        return False

def test_tcp_port(port):
    """Test TCP port connectivity"""
    print_section(f"2. TCP Port {port} Connection Test")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((ESP32_IP, port))
        sock.close()
        
        if result == 0:
            print(f"✓ TCP port {port} is OPEN and accepting connections")
            return True
        else:
            print(f"✗ TCP port {port} is CLOSED or not responding")
            print(f"  Error code: {result}")
            return False
    except socket.timeout:
        print(f"✗ Connection to port {port} timed out after {TIMEOUT}s")
        return False
    except Exception as e:
        print(f"✗ TCP port test error: {e}")
        return False

def test_http_request():
    """Test HTTP GET request"""
    print_section("3. HTTP Request Test")
    url = f"http://{ESP32_IP}"
    
    try:
        print(f"Attempting HTTP GET to {url}...")
        req = urllib.request.Request(url, method='GET')
        
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            status = response.status
            headers = dict(response.headers)
            content = response.read().decode('utf-8', errors='replace')
            
            print(f"✓ HTTP request successful!")
            print(f"\nStatus Code: {status}")
            print(f"\nResponse Headers:")
            for key, value in headers.items():
                print(f"  {key}: {value}")
            print(f"\nResponse Body (first 500 chars):")
            print(content[:500])
            return True
            
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error {e.code}: {e.reason}")
        print(f"  Headers: {dict(e.headers)}")
        return False
    except urllib.error.URLError as e:
        print(f"✗ URL Error: {e.reason}")
        return False
    except socket.timeout:
        print(f"✗ HTTP request timed out after {TIMEOUT}s")
        print("  Possible causes:")
        print("    - Webserver not running on ESP32")
        print("    - ESP32 accepting TCP but not responding to HTTP")
        print("    - Firewall blocking HTTP traffic")
        return False
    except Exception as e:
        print(f"✗ HTTP request error: {e}")
        return False

def test_raw_socket():
    """Test raw socket connection and send HTTP request manually"""
    print_section("4. Raw Socket HTTP Test")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        
        print(f"Connecting to {ESP32_IP}:{HTTP_PORT}...")
        sock.connect((ESP32_IP, HTTP_PORT))
        print("✓ TCP connection established")
        
        # Send HTTP GET request
        http_request = f"GET / HTTP/1.1\r\nHost: {ESP32_IP}\r\nConnection: close\r\n\r\n"
        print(f"\nSending HTTP request:\n{http_request}")
        sock.sendall(http_request.encode())
        
        # Try to receive response
        print("\nWaiting for response...")
        sock.settimeout(TIMEOUT)
        response = b""
        
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
        except socket.timeout:
            pass
        
        sock.close()
        
        if response:
            print(f"✓ Received {len(response)} bytes")
            print(f"\nRaw Response (first 500 bytes):")
            print(response[:500].decode('utf-8', errors='replace'))
            return True
        else:
            print("✗ No response received from server")
            print("  TCP connection succeeded but no HTTP response")
            print("  Possible causes:")
            print("    - Webserver not initialized on ESP32")
            print("    - ESP32 code has bugs preventing HTTP response")
            print("    - Wrong port (check if using port 80)")
            return False
            
    except socket.timeout:
        print(f"✗ Socket operation timed out")
        return False
    except ConnectionRefusedError:
        print(f"✗ Connection refused - port {HTTP_PORT} not listening")
        return False
    except Exception as e:
        print(f"✗ Raw socket test error: {e}")
        return False

def check_arp_table():
    """Check ARP table for MAC address"""
    print_section("5. ARP Table Check")
    try:
        result = subprocess.run(
            ["arp", "-n", ESP32_IP],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if ESP32_IP in result.stdout:
            print("✓ Device found in ARP table")
        else:
            print("⚠ Device not in ARP table (may need ping first)")
    except Exception as e:
        print(f"✗ ARP check error: {e}")

def check_routing():
    """Check routing to ESP32 IP"""
    print_section("6. Routing Information")
    try:
        result = subprocess.run(
            ["netstat", "-rn"],
            capture_output=True,
            text=True
        )
        print("Routing table (filtered for 10.0.0.0 network):")
        for line in result.stdout.split('\n'):
            if '10.0.0' in line or 'Destination' in line:
                print(line)
    except Exception as e:
        print(f"✗ Routing check error: {e}")

def test_serial_monitor(esp32_port):
    """Test serial monitor connection to ESP32"""
    print_section("7. Serial Monitor Test")
    if not esp32_port:
        print("✗ No ESP32 port available for serial test")
        return False
    
    try:
        print(f"Attempting to read serial output from {esp32_port}...")
        print("Waiting 5 seconds for ESP32 startup messages...")
        
        # Use gtimeout if available (from coreutils), otherwise use a different approach
        try:
            # Try gtimeout first (may be installed via homebrew)
            result = subprocess.run(
                ["gtimeout", "5s", "arduino-cli", "monitor", "-p", esp32_port, "-c", "baudrate=115200"],
                capture_output=True,
                text=True,
                timeout=8
            )
        except FileNotFoundError:
            # Fallback: run monitor in background and kill it after 5 seconds
            process = subprocess.Popen(
                ["arduino-cli", "monitor", "-p", esp32_port, "-c", "baudrate=115200"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait 5 seconds
            time.sleep(5)
            
            # Terminate the process
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
            
            result = subprocess.CompletedProcess(
                args=["arduino-cli", "monitor"],
                returncode=0,
                stdout=stdout,
                stderr=stderr
            )
        
        if result.stdout and len(result.stdout.strip()) > 50:
            print("✓ Serial output detected!")
            print("ESP32 Output (last 10 lines):")
            lines = result.stdout.strip().split('\n')[-10:]
            for line in lines:
                if line.strip() and not line.startswith("Monitor port"):
                    print(f"  {line}")
            return True
        else:
            print("✗ No meaningful serial output received")
            if result.stdout:
                print(f"Raw output: {repr(result.stdout[:200])}")
            return False
            
    except Exception as e:
        print(f"✗ Serial monitor test error: {e}")
        return False

def capture_image(num_captures=1):
    """Capture images from ESP32 camera"""
    print_section("8. Camera Image Capture")
    
    # Create captures directory if it doesn't exist
    if not os.path.exists(CAPTURE_DIR):
        os.makedirs(CAPTURE_DIR)
        print(f"✓ Created directory: {CAPTURE_DIR}/")
    
    capture_url = f"http://{ESP32_IP}/capture"
    success_count = 0
    
    for i in range(num_captures):
        try:
            print(f"\nCapturing image {i+1}/{num_captures}...")
            
            # Request image from camera
            req = urllib.request.Request(capture_url, method='GET')
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                if response.status == 200:
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{CAPTURE_DIR}/capture_{timestamp}_{i+1}.jpg"
                    
                    # Save image
                    image_data = response.read()
                    with open(filename, 'wb') as f:
                        f.write(image_data)
                    
                    file_size = len(image_data)
                    print(f"✓ Image saved: {filename} ({file_size} bytes)")
                    success_count += 1
                else:
                    print(f"✗ Failed to capture image {i+1}: HTTP {response.status}")
            
            # Small delay between captures
            if i < num_captures - 1:
                time.sleep(0.5)
                
        except urllib.error.HTTPError as e:
            print(f"✗ HTTP Error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            print(f"✗ URL Error: {e.reason}")
        except socket.timeout:
            print(f"✗ Capture timed out after {TIMEOUT}s")
        except Exception as e:
            print(f"✗ Capture error: {e}")
    
    print(f"\n✓ Successfully captured {success_count}/{num_captures} images")
    return success_count > 0

def main():
    """Run all diagnostic tests"""
    print("\n" + "="*60)
    print("  ESP32S3 Web Server Connectivity Diagnostic")
    print(f"  Target: {ESP32_IP}")
    print("="*60)
    
    # First, detect ESP32 port
    esp32_port = find_esp32_port()
    if not esp32_port:
        print("\n⚠ ESP32 board not detected. Continuing with network tests only...")
    
    results = {}
    
    # Run network tests
    results['ping'] = test_ping()
    results['tcp_port'] = test_tcp_port(HTTP_PORT)
    results['http'] = test_http_request()
    results['raw_socket'] = test_raw_socket()
    
    # Additional checks
    check_arp_table()
    check_routing()
    
    # Run serial test if ESP32 port detected
    if esp32_port:
        results['serial'] = test_serial_monitor(esp32_port)
    else:
        results['serial'] = False
    
    # Try to capture images if HTTP is working
    if results['http']:
        results['camera'] = capture_image(num_captures=3)
    else:
        results['camera'] = False
        print_section("8. Camera Image Capture")
        print("⚠ Skipping camera test - HTTP connection not available")
    
    # Summary
    print_section("DIAGNOSTIC SUMMARY")
    print(f"Ping (ICMP):           {'✓ PASS' if results['ping'] else '✗ FAIL'}")
    print(f"TCP Port {HTTP_PORT}:          {'✓ PASS' if results['tcp_port'] else '✗ FAIL'}")
    print(f"HTTP Request:          {'✓ PASS' if results['http'] else '✗ FAIL'}")
    print(f"Raw Socket HTTP:       {'✓ PASS' if results['raw_socket'] else '✗ FAIL'}")
    print(f"Serial Monitor:        {'✓ PASS' if results['serial'] else '✗ FAIL'}")
    print(f"Camera Capture:        {'✓ PASS' if results['camera'] else '✗ FAIL'}")
    
    print("\n" + "="*60)
    print("DIAGNOSIS:")
    print("="*60)
    
    if esp32_port:
        print(f"ESP32 Port: {esp32_port}")
    
    if results['ping'] and not results['tcp_port']:
        print("⚠ Device responds to ping but TCP port 80 is closed")
        print("  → Webserver likely not started or listening on different port")
        print("  → Check Arduino code: server.begin() called?")
        print("  → Check if using different port (e.g., 8080)")
        
    elif results['tcp_port'] and not results['raw_socket']:
        print("⚠ TCP port is open but not responding to HTTP")
        print("  → Webserver may be stuck or not handling requests")
        print("  → Check ESP32 serial output for errors")
        print("  → Try resetting the ESP32")
        
    elif not results['ping'] and not results['serial']:
        print("✗ Device not responding to ping or serial")
        print("  → Check USB connection and power")
        print("  → Verify ESP32 is powered and running")
        print("  → Try different USB cable or port")
        
    elif not results['ping'] and results['serial']:
        print("⚠ ESP32 is running (serial works) but not on network")
        print("  → WiFi connection failed")
        print("  → Check WiFi credentials and network availability")
        print("  → Static IP may be conflicting")
        
    elif results['http']:
        print("✓ Everything working! Webserver is accessible")
    
    print("\nRECOMMENDED ACTIONS:")
    if esp32_port:
        print(f"1. Check serial output: arduino-cli monitor -p {esp32_port} -c baudrate=115200")
    print("2. Verify Arduino sketch calls server.begin()")
    print("3. Confirm ESP32 is connected to network (not just USB)")
    print("4. Try accessing from browser: http://10.0.0.30")
    print("5. Check if firewall is blocking connections")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
