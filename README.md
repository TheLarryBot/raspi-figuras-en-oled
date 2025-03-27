# 🚀 Detector de Formas con Raspberry Pi y OLED

¡Hola makers! 👋 Soy LarryBot 🤖 de TikTok (@LarryBot_) y este es mi proyecto de detección de formas geométricas usando Raspberry Pi, cámara y pantalla OLED. Perfecto para aprender visión por computadora y electrónica.

## 📹 Mira el demo en TikTok
[![Demo en TikTok](https://img.shields.io/badge/TikTok-@LarryBot_-FF0050?logo=tiktok)](https://www.tiktok.com/@larrybot_)

## 🌟 Características principales
- ✅ Detección de círculos, cuadrados, rectángulos, triángulos y hexágonos
- ✅ Visualización en pantalla OLED con texto grande
- ✅ Procesamiento en tiempo real con la cámara de Raspberry Pi
- ✅ Fácil de modificar y ampliar

## 🛠 Hardware necesario
| Componente | Descripción |
|------------|-------------|
| Raspberry Pi | Modelo 3/4/5 recomendado |
| Cámara | Módulo oficial Raspberry Pi Camera |
| Pantalla OLED | SSD1306 128x64 (I2C) |
| Cableado | Jumpers y protoboard |

![Diagrama de conexión](https://i.imgur.com/JQ6W0gP.png)

## 🔧 Instalación paso a paso

### 1. Instalar dependencias del sistema
```bash
sudo apt update
sudo apt install python3-dev python3-pip libopenblas-dev libatlas-base-dev
sudo apt install libjpeg-dev zlib1g-dev libfreetype6-dev libffi-dev
sudo apt install fonts-dejavu  # Fuentes para el OLED
sudo raspi-config  # Habilitar I2C y Cámara
