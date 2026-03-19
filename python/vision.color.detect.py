import cv2
import numpy as np
import platform
import time


# ==========================================================
# CONFIGURACIÓN
# ==========================================================
# Laptop: True
# UNO Q: False
SHOW_WINDOWS = True

# Laptop: normalmente 0 o 1
# UNO Q: en tus pruebas fue 2
CAMERA_INDEX = 1

FRAME_WIDTH = 640
FRAME_HEIGHT = 360

# --------------------------
# Rangos HSV
# --------------------------
# Naranja
LOWER_ORANGE = np.array([5, 100, 100])
UPPER_ORANGE = np.array([20, 255, 255])

# Blanco
# Ajuste inicial: baja saturación, alto brillo
LOWER_WHITE = np.array([0, 0, 180])
UPPER_WHITE = np.array([179, 70, 255])


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

    # Máscara naranja
    mask_orange = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)

    # Máscara blanca
    mask_white = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)

    # Conteo de pixeles
    orange_pixels = cv2.countNonZero(mask_orange)
    white_pixels = cv2.countNonZero(mask_white)
    total_pixels = mask_orange.size

    orange_ratio = orange_pixels / total_pixels
    white_ratio = white_pixels / total_pixels

    # Resultados filtrados
    result_orange = cv2.bitwise_and(frame, frame, mask=mask_orange)
    result_white = cv2.bitwise_and(frame, frame, mask=mask_white)

    return {
        "hsv": hsv,
        "mask_orange": mask_orange,
        "mask_white": mask_white,
        "result_orange": result_orange,
        "result_white": result_white,
        "orange_pixels": orange_pixels,
        "white_pixels": white_pixels,
        "orange_ratio": orange_ratio,
        "white_ratio": white_ratio,
    }


# ==========================================================
# VISUALIZACIÓN (solo laptop)
# ==========================================================
def show_debug_windows(frame, data):
    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Orange Mask", data["mask_orange"])
    cv2.imshow("White Mask", data["mask_white"])
    cv2.imshow("Orange Filtered Result", data["result_orange"])
    cv2.imshow("White Filtered Result", data["result_white"])


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
    print("Iniciando detección de color naranja y blanco...")
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

            data = process_frame(frame)
            frame_count += 1

            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed

                print(f"FPS: {fps:.2f}")
                print(f"Naranja -> pixeles: {data['orange_pixels']}, ratio: {data['orange_ratio']:.4f}")
                print(f"Blanco  -> pixeles: {data['white_pixels']}, ratio: {data['white_ratio']:.4f}")
                print("-----")

            if SHOW_WINDOWS:
                show_debug_windows(frame, data)

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