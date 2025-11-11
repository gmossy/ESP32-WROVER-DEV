#!/usr/bin/env python3
"""
Generate Arduino config header from .env file
This keeps WiFi credentials out of version control
"""

import os
from pathlib import Path

def load_env(env_file='.env'):
    """Load environment variables from .env file"""
    env_vars = {}
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"⚠️  {env_file} not found. Copy .env.example to .env and configure it.")
        return None
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars

def generate_config_header(env_vars, output_file='config.h'):
    """Generate Arduino config header file"""
    
    # Required variables
    required = ['WIFI_SSID', 'WIFI_PASSWORD', 'ESP32_IP', 'ESP32_GATEWAY', 'ESP32_SUBNET']
    missing = [var for var in required if var not in env_vars]
    
    if missing:
        print(f"❌ Missing required variables in .env: {', '.join(missing)}")
        return False
    
    # Parse IP addresses
    ip_parts = env_vars['ESP32_IP'].split('.')
    gateway_parts = env_vars['ESP32_GATEWAY'].split('.')
    subnet_parts = env_vars['ESP32_SUBNET'].split('.')
    
    header_content = f'''/*
 * Auto-generated configuration file
 * DO NOT EDIT - Generated from .env file
 * Run: python3 generate_config.py
 */

#ifndef CONFIG_H
#define CONFIG_H

// WiFi credentials
const char* ssid = "{env_vars['WIFI_SSID']}";
const char* password = "{env_vars['WIFI_PASSWORD']}";

// Static IP configuration
IPAddress local_IP({', '.join(ip_parts)});
IPAddress gateway({', '.join(gateway_parts)});
IPAddress subnet({', '.join(subnet_parts)});

#endif // CONFIG_H
'''
    
    with open(output_file, 'w') as f:
        f.write(header_content)
    
    print(f"✅ Generated {output_file}")
    print(f"   SSID: {env_vars['WIFI_SSID']}")
    print(f"   IP: {env_vars['ESP32_IP']}")
    return True

def main():
    print("🔧 Generating Arduino configuration from .env...")
    print()
    
    # Load environment variables
    env_vars = load_env()
    if not env_vars:
        return 1
    
    # Generate config for each sketch directory
    sketch_dirs = [
        'camera_webserver',
        'low_power_webserver',
        'webserver',
        'simple'
    ]
    
    success_count = 0
    for sketch_dir in sketch_dirs:
        sketch_path = Path(sketch_dir)
        if sketch_path.exists():
            output_file = sketch_path / 'config.h'
            if generate_config_header(env_vars, output_file):
                success_count += 1
            print()
    
    if success_count > 0:
        print(f"✅ Successfully generated config for {success_count} sketches")
        print()
        print("⚠️  IMPORTANT: config.h files contain your WiFi password!")
        print("   These files are in .gitignore and will NOT be committed.")
        return 0
    else:
        print("❌ Failed to generate any config files")
        return 1

if __name__ == '__main__':
    exit(main())
