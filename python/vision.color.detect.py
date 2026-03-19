import cv2


def open_camera(camera_index=0, width=None, height=None, use_dshow=True):
    if use_dshow:
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        return None

    if width is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)

    if height is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap


def main():
    camera_index = 1   # prueba 0, 1, 2...
    cap = open_camera(camera_index=camera_index, width=640, height=480, use_dshow=True)

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