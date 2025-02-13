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
        if USE_DRONE:
            # Якщо використовується дрон, тут можна отримати тангаж/крен
            pitch = 0  # Замініть на tello.get_pitch(), якщо доступно
            roll = 0   # Замініть на tello.get_roll(), якщо доступно
        else:
            pitch = 0
            roll = 0

        # Малювання ліній горизонту
        cv2.line(frame, 
                 (center_x - horizon_width, horizon_y + int(roll)), 
                 (center_x + horizon_width, horizon_y + int(roll)), 
                 (0, 255, 0), 2)

        # Малювання елементів HUD
        # Фон лівої панелі
        panel_width = 250
        panel_height = 100
        panel_margin = 10
        cv2.rectangle(frame, 
                      (panel_margin, panel_margin), 
                      (panel_width, panel_height), 
                      (0, 0, 0), -1)  # Заповнений прямокутник
        cv2.rectangle(frame, 
                      (panel_margin, panel_margin), 
                      (panel_width, panel_height), 
                      (255, 255, 255), 1)  # Рамка

        # Статус батареї (колір змінюється залежно від рівня)
        battery_color = (0, 255, 0) if battery > 50 else (0, 165, 255) if battery > 20 else (0, 0, 255)
        cv2.putText(frame, f"Battery: {battery}%", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, battery_color, 2)
        # Висота (білий)
        cv2.putText(frame, f"Height: {height}cm", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        # Температура (білий)
        cv2.putText(frame, f"Temp: {temp}°C", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        # Час польоту (білий)
        cv2.putText(frame, f"Flight Time: {flight_time}s", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

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
