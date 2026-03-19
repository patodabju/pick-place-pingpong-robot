import cv2
import platform


def open_camera(camera_index=0, width=640, height=360):
    system_name = platform.system()

    # Selección de backend según sistema operativo
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
    camera_index = 2   # En tu UNO Q ya comprobaste que este índice funciona

    cap = open_camera(camera_index=camera_index, width=640, height=360)

    if cap is None:
        print(f"Error: no se pudo abrir la cámara con índice {camera_index}.")
        return

    print(f"Cámara abierta correctamente con índice {camera_index}.")
    print("Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: no se pudo leer un frame de la cámara.")
            break

        cv2.imshow("Camera Feed", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()