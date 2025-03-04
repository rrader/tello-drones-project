import cv2
from djitellopy import Tello
import os
import glob
import time

# Конфігурація
USE_DRONE = False  # Встановіть False для використання локальних зображень
SCENE_FOLDER = 'scene1'
TARGET_FPS = 5  # Цільова частота кадрів для зображень з папки

if USE_DRONE:
    # Ініціалізація дрона Tello
    tello = Tello()
    tello.connect()
    
    # Запуск відеопотоку
    tello.streamon()
    frame_read = tello.get_frame_read()
else:
    # Отримання списку зображень з папки сцени
    image_files = sorted(glob.glob(os.path.join(SCENE_FOLDER, '*.jpg')))
    print(image_files)
    if not image_files:
        raise ValueError(f"Зображення не знайдені в {SCENE_FOLDER}")
    current_image_index = 0

# Безперервне читання та відображення кадрів
try:
    prev_time = time.time()
    while True:
        current_time = time.time()
        
        if USE_DRONE:
            # Отримання поточного кадру з дрона
            frame = frame_read.frame
            # Отримання інформації про стан дрона
            battery = tello.get_battery()
            height = tello.get_height()
            temp = tello.get_temperature()
            flight_time = tello.get_flight_time()
            # Додаємо швидкість (якщо доступно)
            speed = 0  # Замініть на tello.get_speed(), якщо доступно
            
            # Отримання даних гіроскопа
            state = tello.get_current_state()
            pitch = state.get('pitch', 0)
            roll = state.get('roll', 0)
            yaw = state.get('yaw', 0)
        else:
            # Контроль частоти кадрів для зображень з папки
            time_elapsed = current_time - prev_time
            if time_elapsed < 1.0/TARGET_FPS:
                continue
                
            # Читання зображення з папки
            frame = cv2.imread(image_files[current_image_index])
            current_image_index = (current_image_index + 1) % len(image_files)
            # Заповнювачі значень для режиму без дрона
            battery = 100
            height = 0
            temp = 25
            flight_time = 0
            speed = 0  # Заповнювач для швидкості
            
            # Симуляція даних гіроскопа для режиму без дрона
            import math
            pitch = 5 * math.sin(current_time * 0.5)  # Симуляція коливань
            roll = 3 * math.cos(current_time * 0.7)
            yaw = (current_time * 10) % 360  # Поступове обертання
        
        # Розрахунок та відображення FPS
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        
        # Отримання розмірів кадру
        height_frame, width_frame = frame.shape[:2]
        center_x, center_y = width_frame // 2, height_frame // 2

        # Малювання рамки
        border_thickness = 2
        cv2.rectangle(frame, (0, 0), (width_frame-1, height_frame-1), (255, 255, 255), border_thickness)

        # Малювання перехрестя
        crosshair_size = 20
        crosshair_color = (0, 255, 0)  # Зелений
        cv2.line(frame, (center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y), crosshair_color, 2)
        cv2.line(frame, (center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size), crosshair_color, 2)

        # Малювання штучного горизонту (індикатор рівня)
        horizon_width = 100
        horizon_y = center_y

        # Малювання ліній горизонту
        cv2.line(frame, 
                 (center_x - horizon_width, horizon_y + int(roll)), 
                 (center_x + horizon_width, horizon_y + int(roll)), 
                 (0, 255, 0), 2)

        panel_width = 250  
        panel_height = 230 
        panel_margin = 20
        panel_x = panel_margin  
        panel_y = panel_margin

        panel_overlay = frame.copy()
        cv2.rectangle(panel_overlay, 
                     (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     (40, 40, 80), -1)  # Темно-синій фон

        alpha = 0.7  
        cv2.addWeighted(panel_overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Додавання рамки з градієнтом
        cv2.rectangle(frame, 
                     (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     (100, 100, 180), 2)  # Світло-синя рамка
        
        # Кольори тексту
        text_color = (220, 220, 240) 
        highlight_color = (180, 255, 255) 
        
        # Заголовок панелі
        cv2.putText(frame, "DRONE TELEMETRY", (panel_x + 25, panel_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, highlight_color, 2)
        
        # Відображення інформації
        # Швидкість
        cv2.putText(frame, f"Speed:", (panel_x + 10, panel_y + 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1)
        cv2.putText(frame, f"{speed} km/h", (panel_x + 150, panel_y + 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, highlight_color, 1)
                   
        # Батарея (колір змінюється залежно від рівня)
        battery_color = (0, 255, 0) if battery > 50 else (0, 165, 255) if battery > 20 else (0, 0, 255)
        cv2.putText(frame, f"Battery:", (panel_x + 10, panel_y + 85), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1)
        cv2.putText(frame, f"{battery}%", (panel_x + 150, panel_y + 85), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, battery_color, 1)
                   
        # Висота
        cv2.putText(frame, f"Altitude:", (panel_x + 10, panel_y + 115), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1)
        cv2.putText(frame, f"{height} cm", (panel_x + 150, panel_y + 115), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, highlight_color, 1)
                   
        # Температура
        cv2.putText(frame, f"Temperature:", (panel_x + 10, panel_y + 145), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1)
        cv2.putText(frame, f"{temp}°C", (panel_x + 150, panel_y + 145), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, highlight_color, 1)
        
        # Додавання даних гіроскопа
        cv2.putText(frame, f"Pitch:", (panel_x + 10, panel_y + 175), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1)
        cv2.putText(frame, f"{pitch:.1f}°", (panel_x + 150, panel_y + 175), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, highlight_color, 1)
                   
        cv2.putText(frame, f"Roll:", (panel_x + 10, panel_y + 205), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1)
        cv2.putText(frame, f"{roll:.1f}°", (panel_x + 150, panel_y + 205), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, highlight_color, 1)
                   
        cv2.putText(frame, f"Yaw:", (panel_x + 10, panel_y + 235), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1)
        cv2.putText(frame, f"{yaw:.1f}°", (panel_x + 150, panel_y + 235), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, highlight_color, 1)

        # Малювання сторін світу
        directions = ['N', 'E', 'S', 'W']
        direction_positions = [
            (center_x, 30),  # Північ
            (width_frame - 30, center_y),  # Схід
            (center_x, height_frame - 30),  # Південь
            (30, center_y)  # Захід
        ]
        for direction, pos in zip(directions, direction_positions):
            cv2.putText(frame, direction, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Відображення кадру у вікні
        cv2.imshow("Tello Live Feed", frame)
        
        # Очікування 1 мс та перевірка натискання клавіші 'q' для виходу
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Безпечне закриття відеопотоку та всіх відкритих вікон
    if USE_DRONE:
        tello.streamoff()
    cv2.destroyAllWindows()
