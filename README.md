# NuttyFi32 — Arduino Boards Package for NuttyFi32 (Custom NuttyFi Board)

<p align="left">
  <a href="https://www.nuttyengineer.com/">
    <img src="https://img.shields.io/badge/NuttyFi32-Arduino%20Boards%20Package-0d6efd?style=for-the-badge" 
         alt="NuttyFi32" />
  </a>
  <img src="https://www.smedehradun.com/wp-content/uploads/2020/07/cropped-SME-origional-logo.png"
       alt="SME Dehradun" height="28" style="vertical-align: middle; margin-left: 6px; margin-right: 6px;" />
  <img src="https://img.shields.io/badge/Invented%20by-SME%20Dehradun-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Made%20in-Bharat-orange?style=for-the-badge" />
</p>

The **NuttyFi32 (ESP32)** is a custom-designed IoT board built for stable Wi-Fi, Bluetooth, high-performance edge computing, and secure cloud communication.  
This repository provides the **Arduino Boards Package** for NuttyFi32 with full Boards Manager support.

---

## Install in Arduino IDE 2.x

1. Open **File → Preferences → Additional Boards Manager Link / URLs** and add:

   ```text
   https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package_nuttyfi32_index.json


### 2️⃣ Open Boards Manager  
**Tools → Board → Boards Manager…**  
Search for **NuttyFi32** → **Install**

### 3️⃣ Select Your Board  
**Tools → Board → NuttyFi32 → NuttyFi32 (ESP32 Custom Board)**

---

# 📦 Package Status

![GitHub release](https://img.shields.io/github/v/release/itsbhupendrasingh/nuttyfi32)
![GitHub Release Date](https://img.shields.io/github/release-date/itsbhupendrasingh/nuttyfi32)
![Downloads](https://img.shields.io/github/downloads/itsbhupendrasingh/nuttyfi32/latest/total)
![Platform](https://img.shields.io/badge/Platform-Arduino%20IDE%202.x-00979D?logo=arduino)
![ESP32](https://img.shields.io/badge/Core-ESP32-blue?logo=espressif)

---

# 🎯 Features Included in This Package

✔ NuttyFi32 **variant configuration**  
✔ **Pin mapping** for your custom PCB  
✔ **Optimized flash partitions**  
✔ **LittleFS / SPIFFS support**  
✔ **Wi-Fi, BLE, OTA examples**  
✔ **Board-specific settings** for stable uploads  

This package is built on top of the official ESP32 Arduino core:  
➡ https://github.com/espressif/arduino-esp32

---

# 🧭 Quick Links


* **Boards Manager URL:**
  ```text
   https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package_nuttyfi32_index.json


### Boards
### Issues & Support  
https://github.com/itsbhupendrasingh/nuttyfi32/issues



# 🚀 Getting Started

## 🔹 Blink Example - Inbuilt LED

```cpp
#const int LED_PIN = 13;   // NuttyFi32 built-in LED

void setup() {
  Serial.begin(115200);
  delay(50);
  Serial.println("Simple blink start on NuttyFi32");
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);   // LED ON
  Serial.println("LED ON");
  delay(1000);

  digitalWrite(LED_PIN, LOW);    // LED OFF
  Serial.println("LED OFF");
  delay(1000);
}

```

## 🔹 LED Fade Example - Inbuilt LED

```cpp
const int LED_PIN = 13;      // Built-in LED on NuttyFi32
const int PWM_CH = 0;        // Channel 0–15
const int PWM_FREQ = 5000;   // 5 kHz
const int PWM_RES = 8;       // 8-bit (0–255)

int brightness = 0;
int fadeAmount = 5;

void setup() {
  Serial.begin(115200);
  delay(200);   // small delay for serial monitor

  Serial.println("NuttyFi32 LED Fade Example Started");

  ledcSetup(PWM_CH, PWM_FREQ, PWM_RES);
  ledcAttachPin(LED_PIN, PWM_CH);
}

void loop() {
  ledcWrite(PWM_CH, brightness);

  // print current brightness
  Serial.print("Brightness: ");
  Serial.println(brightness);

  brightness += fadeAmount;

  if (brightness <= 0 || brightness >= 255) {
    fadeAmount = -fadeAmount;
  }

  delay(30);
}

```
