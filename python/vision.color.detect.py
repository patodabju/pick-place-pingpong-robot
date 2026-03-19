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
    camera_index = 1  # laptop (ajústalo a 2 en UNO Q)

    cap = open_camera(camera_index)

    if cap is None:
        print("Error al abrir cámara")
        return

    print("Cámara OK - iniciando captura + HSV")

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error leyendo frame")
                break

            # 🔥 NUEVO: conversión a HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            frame_count += 1

            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed

                print(f"FPS: {fps:.2f}")
                print(f"Frame shape: {frame.shape}")
                print(f"HSV shape: {hsv.shape}")
                print("-----")

    except KeyboardInterrupt:
        print("Stop manual")

    cap.release()


if __name__ == "__main__":
    main()