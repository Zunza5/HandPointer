import pyautogui
import webcam
import threading
import globals
import time
import math
from numpy.linalg import norm
import numpy as np

def collect_marker_data(fingermarkers, clickmarker):
    
    if globals.detection_result is not None and len(globals.detection_result.hand_landmarks) > 0:
        fingermarker = []
        clickmarker.clear()
        fingermarker.append(globals.detection_result.hand_landmarks[0][8])
        fingermarker.append(int(time.time_ns() / 1_000_000))
        fingermarkers.append(fingermarker)
        clickmarker.append(globals.detection_result.hand_landmarks[0][4])
        clickmarker.append(globals.detection_result.hand_landmarks[0][12])

        return True
    


def calculate_velocity(fingermarkers):
    
    # Calcola la velocità tra 2 campioni
    if len(fingermarkers) < 2:
        return 0, 0, 0

    #calcolo spazio percorso
    

    screenWidth, screenHeight = pyautogui.size()
    sensitivity = 1
    p1 = fingermarkers[-1][0]
    t1 = fingermarkers[-1][1]
    p0 = fingermarkers[-2][0]
    t0 = fingermarkers[-2][1]
    dx_norm = p1.x - p0.x
    dy_norm = p1.y - p0.y
    dt = max(t1 - t0, 1e-4)
    dx_pixel = dx_norm * screenWidth * sensitivity
    dy_pixel = dy_norm * screenHeight * sensitivity
    dx_avg = dx_pixel
    dy_avg = dy_pixel

    

    # Acceleratore (gain sigmoidale)
    g_min, g_max = 0.7, 2.6
    v_mid, k = 80.0, 0.035
    speed = math.hypot(dx_avg, dy_avg)
    G = g_min + (g_max - g_min) / (1 + math.exp(-k * (speed - v_mid)))
    dx_acc = dx_avg * G
    dy_acc = dy_avg * G

    # Filtro EMA per dx e dy
    if not hasattr(calculate_velocity, "ema_dx"):
        calculate_velocity.ema_dx = dx_acc
        calculate_velocity.ema_dy = dy_acc
    alpha = 0.8  # coefficiente di smoothing
    calculate_velocity.ema_dx = alpha * dx_acc + (1 - alpha) * calculate_velocity.ema_dx
    calculate_velocity.ema_dy = alpha * dy_acc + (1 - alpha) * calculate_velocity.ema_dy
    dx_filt = calculate_velocity.ema_dx
    dy_filt = calculate_velocity.ema_dy

    # Limitatore di velocità massima proporzionale alla sensibilità
    base_speed = 120  # valore di riferimento
    max_speed = base_speed * sensitivity
    speed = math.hypot(dx_filt, dy_filt)
    if speed > max_speed:
        scale = max_speed / speed
        dx_filt *= scale
        dy_filt *= scale

    # Zona morta: se il movimento è troppo piccolo, annulla
    dead_zone = 7 * sensitivity  # pixel, regola a piacere
    if math.hypot(dx_filt, dy_filt) < dead_zone:
        return 0, 0, 0
    
    

    return int(dx_filt), int(dy_filt), int(dt/1000)


def main():
    thread = threading.Thread(target=webcam.init_mediapipe)
    thread.start()
    fingermarkers = []
    clickmarker = []
    img_counter = 0
    clickable = True
    screenWidth, screenHeight = pyautogui.size()

    while True:
        if collect_marker_data(fingermarkers, clickmarker):
            if len(fingermarkers) >= 2:
                x, y = pyautogui.position()
                dx, dy, dt = calculate_velocity(fingermarkers)
                if(x + dx > 0 and x + dx < screenWidth and y + dy > 0 and y + dy < screenHeight):
                    pyautogui.moveTo(x + dx, y + dy, dt)
                # Mantieni solo gli ultimi 2 marker
                fingermarkers = fingermarkers[-2:]

                # Distanza euclidea 3D tra pollice e medio
                p1 = clickmarker[-1]
                p2 = clickmarker[-2]
                dist3d = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
                print(f"3D distance between thumb and middle finger: {dist3d}")
                if dist3d < 0.04 and clickable:
                    # Esegui il click
                    pyautogui.click()
                    clickable = False
                elif dist3d >= 0.04:
                    clickable = True
        else:
            fingermarkers.clear()
            clickmarker.clear()



if __name__ == "__main__":
    main()




