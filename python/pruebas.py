import cv2


def test_camera(index):
    print(f"Probando cámara en índice {index}...")
    cap = cv2.VideoCapture(index)

    if not cap.isOpened():
        print(f"  No se pudo abrir índice {index}")
        return False

    ret, frame = cap.read()
    if not ret:
        print(f"  Se abrió índice {index}, pero no entrega frames")
        cap.release()
        return False

    print(f"  Índice {index} OK")
    print(f"  Resolución detectada: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
    return True


def main():
    found = False

    for i in range(6):
        ok = test_camera(i)
        if ok:
            found = True

    if not found:
        print("No se encontró ninguna cámara funcional.")


if __name__ == "__main__":
    main()