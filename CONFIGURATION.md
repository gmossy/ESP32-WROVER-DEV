# 🔐 Configuration Guide

This project uses environment variables to keep WiFi credentials and sensitive data out of version control.

## 🚀 Quick Setup

### 1. Create Your .env File

```bash
cp .env.example .env
```

### 2. Edit .env with Your WiFi Credentials

```bash
nano .env
# or
code .env
```

Update these values:
```env
WIFI_SSID=YOUR_ACTUAL_WIFI_NAME
WIFI_PASSWORD=YOUR_ACTUAL_PASSWORD
ESP32_IP=10.0.0.30
```

### 3. Generate Arduino Config Files

```bash
python3 generate_config.py
```

This creates `config.h` files in each sketch directory with your WiFi credentials.

### 4. Upload to ESP32

```bash
cd camera_webserver
arduino-cli compile --fqbn esp32:esp32:esp32wrover .
arduino-cli upload --fqbn esp32:esp32:esp32wrover --port /dev/cu.usbserial-143130 --upload-property upload.speed=115200 .
```

## 📁 Files Explained

### `.env` (NOT in git)
Contains your actual WiFi credentials and configuration. **Never commit this file!**

### `.env.example` (in git)
Template showing what variables are needed. Safe to commit.

### `config.h` (NOT in git, auto-generated)
Arduino header file with WiFi credentials. Generated from `.env` by `generate_config.py`.

### `generate_config.py`
Python script that reads `.env` and creates `config.h` files for each Arduino sketch.

## 🔒 Security

### What's Protected

✅ `.env` - In .gitignore, never committed
✅ `config.h` - In .gitignore, never committed  
✅ Your WiFi password - Never in version control

### What's in Git

✅ `.env.example` - Template only
✅ `generate_config.py` - Config generator script
✅ Arduino sketches - Without credentials

## 🛠️ How It Works

1. **You create** `.env` with your WiFi credentials
2. **You run** `python3 generate_config.py`
3. **Script generates** `config.h` in each sketch folder
4. **Arduino sketches** include `config.h` for WiFi credentials
5. **Git ignores** both `.env` and `config.h` files

## 📝 Configuration Variables

### WiFi Settings
```env
WIFI_SSID=YourNetworkName          # Your WiFi network name
WIFI_PASSWORD=YourPassword         # Your WiFi password
```

### ESP32 Network
```env
ESP32_IP=10.0.0.30                # Static IP for ESP32
ESP32_GATEWAY=10.0.0.1            # Your router IP
ESP32_SUBNET=255.255.255.0        # Subnet mask
```

### n8n Configuration
```env
N8N_BASIC_AUTH_USER=admin         # n8n username
N8N_BASIC_AUTH_PASSWORD=changeme  # n8n password (change this!)
```

### Image Viewer
```env
PORT=8080                         # Web server port
CAPTURE_DIR=captures              # Image storage folder
```

## 🔄 Updating Configuration

### Change WiFi Network

1. Edit `.env` file
2. Run `python3 generate_config.py`
3. Re-upload sketch to ESP32

### Change Static IP

1. Edit `ESP32_IP` in `.env`
2. Run `python3 generate_config.py`
3. Re-upload sketch to ESP32
4. Update `ESP32_IP` in docker-compose.yml if using Docker

## 🐛 Troubleshooting

### "config.h: No such file"

**Problem:** Arduino sketch can't find config.h

**Solution:**
```bash
python3 generate_config.py
```

### "Missing required variables in .env"

**Problem:** .env file is incomplete

**Solution:** Check .env.example for all required variables and add them to .env

### "WiFi connection failed"

**Problem:** Wrong credentials or network unavailable

**Solution:**
1. Verify SSID and password in .env
2. Ensure using 2.4GHz network (ESP32 doesn't support 5GHz)
3. Check WiFi signal strength
4. Run `python3 generate_config.py` again
5. Re-upload sketch

### ".env not found"

**Problem:** No .env file exists

**Solution:**
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

## 📋 Checklist for New Setup

- [ ] Copy .env.example to .env
- [ ] Edit .env with your WiFi credentials
- [ ] Run `python3 generate_config.py`
- [ ] Verify config.h files were created
- [ ] Upload sketch to ESP32
- [ ] Test WiFi connection

## 🔐 Best Practices

1. **Never commit .env or config.h**
   - Already in .gitignore
   - Double-check before pushing

2. **Use strong passwords**
   - Especially for n8n
   - Change default passwords

3. **Keep .env.example updated**
   - Add new variables to .env.example
   - Remove sensitive values

4. **Document changes**
   - Update this file when adding new config options
   - Keep .env.example in sync

## 🆘 Need Help?

1. Check that .env exists: `ls -la .env`
2. Verify .env format: `cat .env`
3. Run config generator: `python3 generate_config.py`
4. Check generated files: `ls -la */config.h`

---

**Remember:** Your WiFi password is never stored in git! 🔒

*Built with ❤️ by Glenn Mossy*
