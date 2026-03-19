import cv2
import platform
import time


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


def main():
    camera_index = 2

    cap = open_camera(camera_index)

    if cap is None:
        print(f"Error: no se pudo abrir la cámara con índice {camera_index}")
        return

    print("Cámara abierta correctamente (modo headless)")
    print("Leyendo frames... (Ctrl+C para salir)")

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error al leer frame")
                break

            frame_count += 1

            # Cada 30 frames mostramos info (debug)
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"FPS aproximado: {fps:.2f}")

    except KeyboardInterrupt:
        print("Interrupción manual")

    cap.release()


if __name__ == "__main__":
    main()