import cv2
import numpy as np
import platform
import time


# ==========================================================
# CONFIGURACIÓN
# ==========================================================
# En laptop: True
# En UNO Q: False
SHOW_WINDOWS = True

# Índices sugeridos:
# Laptop: normalmente 0 o 1
# UNO Q: en tus pruebas fue 2
CAMERA_INDEX = 1

FRAME_WIDTH = 640
FRAME_HEIGHT = 360

# Rango HSV inicial para naranja
# Luego lo ajustamos si hace falta
LOWER_ORANGE = np.array([5, 100, 100])
UPPER_ORANGE = np.array([20, 255, 255])


# ==========================================================
# APERTURA DE CÁMARA
# ==========================================================
def open_camera(camera_index=0, width=640, height=360):
    system_name = platform.system()

    if system_name == "Windows":
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)

    if not cap.isOpened():
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap


# ==========================================================
# PROCESAMIENTO DE FRAME
# ==========================================================
def process_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_orange = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)

    detected_pixels = cv2.countNonZero(mask_orange)
    total_pixels = mask_orange.size
    ratio = detected_pixels / total_pixels

    result = cv2.bitwise_and(frame, frame, mask=mask_orange)

    return hsv, mask_orange, result, detected_pixels, ratio


# ==========================================================
# VISUALIZACIÓN (solo laptop)
# ==========================================================
def show_debug_windows(frame, mask, result):
    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Orange Mask", mask)
    cv2.imshow("Filtered Result", result)


# ==========================================================
# MAIN
# ==========================================================
def main():
    cap = open_camera(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)

    if cap is None:
        print(f"Error: no se pudo abrir la cámara con índice {CAMERA_INDEX}")
        return

    mode = "visual" if SHOW_WINDOWS else "headless"
    print(f"Cámara abierta correctamente en modo {mode}")
    print("Iniciando detección de color naranja...")
    if SHOW_WINDOWS:
        print("Presiona 'q' para salir.")

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error: no se pudo leer un frame de la cámara.")
                break

            hsv, mask_orange, result, detected_pixels, ratio = process_frame(frame)

            frame_count += 1

            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed

                print(f"FPS: {fps:.2f}")
                print(f"Frame shape: {frame.shape}")
                print(f"HSV shape: {hsv.shape}")
                print(f"Detección naranja: {detected_pixels} pixeles")
                print(f"Ratio: {ratio:.4f}")
                print("-----")

            if SHOW_WINDOWS:
                show_debug_windows(frame, mask_orange, result)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

    except KeyboardInterrupt:
        print("Interrupción manual.")

    cap.release()

    if SHOW_WINDOWS:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()