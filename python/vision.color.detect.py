import cv2
import numpy as np
import platform
import time


# ==========================================================
# CONFIGURACIÓN
# ==========================================================
SHOW_WINDOWS = True

# Laptop: normalmente 0 o 1
# UNO Q: en tus pruebas fue 2
CAMERA_INDEX = 1

FRAME_WIDTH = 640
FRAME_HEIGHT = 360

# Área mínima para considerar un objeto válido
MIN_OBJECT_AREA = 500

# Rangos HSV
LOWER_ORANGE = np.array([5, 100, 100])
UPPER_ORANGE = np.array([20, 255, 255])

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
# UTILIDADES DE MÁSCARA
# ==========================================================
def clean_mask(mask):
    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def get_largest_object(mask, min_area=500):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    largest_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest_contour)

    if area < min_area:
        return None

    M = cv2.moments(largest_contour)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    x, y, w, h = cv2.boundingRect(largest_contour)

    return {
        "contour": largest_contour,
        "area": area,
        "center": (cx, cy),
        "bbox": (x, y, w, h),
    }


# ==========================================================
# PROCESAMIENTO DE FRAME
# ==========================================================
def process_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Máscaras base
    mask_orange = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)
    mask_white = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)

    # Limpieza
    mask_orange = clean_mask(mask_orange)
    mask_white = clean_mask(mask_white)

    # Conteo general
    orange_pixels = cv2.countNonZero(mask_orange)
    white_pixels = cv2.countNonZero(mask_white)
    total_pixels = mask_orange.size

    orange_ratio = orange_pixels / total_pixels
    white_ratio = white_pixels / total_pixels

    # Objetos principales
    orange_object = get_largest_object(mask_orange, MIN_OBJECT_AREA)
    white_object = get_largest_object(mask_white, MIN_OBJECT_AREA)

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
        "orange_object": orange_object,
        "white_object": white_object,
    }


# ==========================================================
# DIBUJO
# ==========================================================
def draw_object_overlay(frame, obj, label, color_bgr):
    if obj is None:
        return frame

    x, y, w, h = obj["bbox"]
    cx, cy = obj["center"]
    area = obj["area"]

    cv2.rectangle(frame, (x, y), (x + w, y + h), color_bgr, 2)
    cv2.circle(frame, (cx, cy), 5, color_bgr, -1)

    text_1 = f"{label}"
    text_2 = f"({cx}, {cy}) A={int(area)}"

    cv2.putText(frame, text_1, (x, y - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2)
    cv2.putText(frame, text_2, (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_bgr, 2)

    return frame


def build_annotated_frame(frame, data):
    annotated = frame.copy()

    annotated = draw_object_overlay(annotated, data["orange_object"], "Orange", (0, 165, 255))
    annotated = draw_object_overlay(annotated, data["white_object"], "White", (255, 255, 255))

    return annotated


# ==========================================================
# VISUALIZACIÓN (solo laptop)
# ==========================================================
def show_debug_windows(frame, data):
    annotated = build_annotated_frame(frame, data)

    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Annotated Feed", annotated)
    cv2.imshow("Orange Mask", data["mask_orange"])
    cv2.imshow("White Mask", data["mask_white"])
    cv2.imshow("Orange Filtered Result", data["result_orange"])
    cv2.imshow("White Filtered Result", data["result_white"])


# ==========================================================
# IMPRESIÓN DE DEBUG
# ==========================================================
def print_object_info(name, obj):
    if obj is None:
        print(f"{name}: no detectado")
    else:
        cx, cy = obj["center"]
        print(f"{name}: centro=({cx}, {cy}), area={obj['area']:.1f}")


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
    print("Iniciando detección y localización de objetos...")
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
                print_object_info("Naranja", data["orange_object"])
                print(f"Blanco  -> pixeles: {data['white_pixels']}, ratio: {data['white_ratio']:.4f}")
                print_object_info("Blanco", data["white_object"])
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