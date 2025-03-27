from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from picamera2 import Picamera2
import time

# Configuración OLED
OLED_WIDTH = 128
OLED_HEIGHT = 64

# Configuración de la cámara
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

# Mapeo de figuras a nombres completos
SHAPE_TO_NAME = {
    "circle": "CIRCULO",
    "square": "CUADRADO",
    "rectangle": "RECTANGULO",
    "triangle": "TRIANGULO",
    "hexagon": "HEXAGONO"
}

MIN_CONTOUR_AREA = 300
FONT_SCALE = 0.7  # Escala para texto en imagen de cámara

def init_oled():
    """Inicializa el dispositivo OLED con fuente grande"""
    try:
        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial)
        
        # Intentar cargar fuente grande (instalar con: sudo apt install fonts-dejavu)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)  # Fuente más grande
        except:
            # Si falla, usar fuente por defecto más grande posible
            font = ImageFont.load_default()
            print("Instala 'sudo apt install fonts-dejavu' para mejor visualización")
        
        return device, font
    except Exception as e:
        print(f"Error inicializando OLED: {e}")
        return None, None

def show_on_oled(device, font, text_lines):
    """Muestra texto grande en la pantalla OLED"""
    if device is None:
        return
        
    try:
        # Crear imagen
        image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
        draw = ImageDraw.Draw(image)
        
        # Calcular posición vertical centrada
        total_height = len(text_lines) * 24  # 24px por línea
        y_pos = (OLED_HEIGHT - total_height) // 2
        
        for line in text_lines:
            # Acortar línea si es muy larga
            line = line[:10]  # Máximo 10 caracteres por línea
            
            # Calcular ancho del texto
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Centrar horizontalmente
            x_pos = (OLED_WIDTH - text_width) // 2
            
            # Dibujar texto
            draw.text((x_pos, y_pos), line, font=font, fill="white")
            y_pos += 24  # Espaciado entre líneas
        
        device.display(image)
    except Exception as e:
        print(f"Error mostrando en OLED: {e}")

def detect_shape(c):
    """Detecta la forma del contorno"""
    shape = "unidentified"
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.04 * peri, True)
    vertices = len(approx)

    if vertices == 3:
        shape = "triangle"
    elif vertices == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
        aspect_ratio = w / float(h)
        shape = "square" if 0.9 <= aspect_ratio <= 1.1 else "rectangle"
    elif vertices == 6:
        shape = "hexagon"
    elif vertices > 8:  # Más sensible para círculos
        area = cv2.contourArea(c)
        circularity = 4 * np.pi * area / (peri * peri) if peri > 0 else 0
        if circularity > 0.7:
            shape = "circle"

    return shape

def main():
    oled, font = init_oled()
    picam2.start()
    
    try:
        while True:
            # Capturar y procesar imagen
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Procesamiento para detección
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (7, 7), 1.5)
            edged = cv2.Canny(blurred, 30, 100)
            
            # Mejorar contornos
            kernel = np.ones((3,3), np.uint8)
            edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Detección de formas
            detected_shapes = []
            for c in contours:
                if cv2.contourArea(c) < MIN_CONTOUR_AREA:
                    continue
                
                shape = detect_shape(c)
                if shape == "unidentified":
                    continue
                
                # Dibujar en frame de cámara
                cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                M = cv2.moments(c)
                cX = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0
                cY = int(M["m01"] / M["m00"]) if M["m00"] != 0 else 0
                cv2.putText(frame, shape, (cX, cY), 
                           cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, 
                           (255, 255, 255), 2)
                
                detected_shapes.append(shape)
            
            # Actualizar OLED con texto grande
            if detected_shapes:
                shape_name = SHAPE_TO_NAME.get(detected_shapes[0], "DESCONOCIDO")
                show_on_oled(oled, font, [shape_name])
            else:
                show_on_oled(oled, font, ["NO DETECTADO"])
            
            # Mostrar ventana de cámara
            cv2.imshow('Deteccion de Formas', frame)
            
            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            time.sleep(0.05)
            
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        if oled:
            oled.clear()

if __name__ == "__main__":
    main()
