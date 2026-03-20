import cv2
import numpy as np
import platform
import time


# ==========================================================
# CONFIGURACIÓN
# ==========================================================
SHOW_WINDOWS = True
CAMERA_INDEX = 0          # Laptop: 0 o 1 | UNO Q: el índice que ya encontraste
FRAME_WIDTH = 640
FRAME_HEIGHT = 360

# Dimensiones reales del workspace útil (dentro del tape)
WORKSPACE_WIDTH_CM = 36.4
WORKSPACE_HEIGHT_CM = 24.6

# Escala solo para la vista warp (px por cm)
WARP_SCALE = 20

# Rangos HSV
LOWER_ORANGE = np.array([5, 100, 100])
UPPER_ORANGE = np.array([20, 255, 255])

LOWER_WHITE = np.array([0, 0, 180])
UPPER_WHITE = np.array([179, 70, 255])

LOWER_BLUE = np.array([85, 80, 80])
UPPER_BLUE = np.array([115, 255, 255])

MIN_OBJECT_AREA = 500


# ==========================================================
# CÁMARA
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

    # Intento de desactivar auto white balance si la cámara lo soporta
    cap.set(cv2.CAP_PROP_AUTO_WB, 0)

    return cap


# ==========================================================
# UTILIDADES GENERALES
# ==========================================================
def clean_mask(mask):
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def order_points(pts):
    """
    Ordena 4 puntos como:
    [top-left, top-right, bottom-right, bottom-left]
    """
    pts = np.array(pts, dtype=np.float32)

    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    top_left = pts[np.argmin(s)]
    bottom_right = pts[np.argmax(s)]
    top_right = pts[np.argmin(diff)]
    bottom_left = pts[np.argmax(diff)]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)


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
# DETECCIÓN DEL WORKSPACE
# ==========================================================
def detect_workspace(frame):
    """
    Detecta el área útil como la mayor región oscura interior.
    Esto evita depender del color exacto del tape o de la hoja blanca.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar la zona negra del workspace
    # Ajustable si hace falta
    _, dark_mask = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((7, 7), np.uint8)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, dark_mask

    # Buscar el contorno oscuro más grande razonable
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    workspace_contour = None
    workspace_quad = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 10000:
            continue

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        # Si encontramos 4 puntos, perfecto
        if len(approx) == 4:
            workspace_contour = cnt
            workspace_quad = approx.reshape(4, 2)
            break

    # Si no salió cuadrilátero, usamos rectángulo mínimo del mayor contorno
    if workspace_quad is None:
        cnt = contours[0]
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        workspace_quad = np.array(box, dtype=np.float32)
        workspace_contour = cnt

    ordered = order_points(workspace_quad)

    return {
        "contour": workspace_contour,
        "corners": ordered,   # TL, TR, BR, BL
    }, dark_mask


def draw_workspace_overlay(frame, workspace):
    if workspace is None:
        return frame

    out = frame.copy()
    corners = workspace["corners"].astype(int)

    # Dibujar contorno
    cv2.polylines(out, [corners], isClosed=True, color=(0, 255, 0), thickness=2)

    # Etiquetar esquinas
    labels = ["TL", "TR", "BR", "BL"]
    for pt, label in zip(corners, labels):
        cv2.circle(out, tuple(pt), 6, (0, 255, 255), -1)
        cv2.putText(out, label, (pt[0] + 5, pt[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    # Origen = esquina inferior izquierda (BL)
    origin = tuple(corners[3])
    cv2.circle(out, origin, 8, (0, 0, 255), -1)
    cv2.putText(out, "Origin (0,0)", (origin[0] + 10, origin[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    return out


def warp_workspace(frame, workspace):
    if workspace is None:
        return None, None

    corners = workspace["corners"].astype(np.float32)

    warp_w = int(WORKSPACE_WIDTH_CM * WARP_SCALE)
    warp_h = int(WORKSPACE_HEIGHT_CM * WARP_SCALE)

    dst = np.array([
        [0, 0],
        [warp_w - 1, 0],
        [warp_w - 1, warp_h - 1],
        [0, warp_h - 1]
    ], dtype=np.float32)

    H = cv2.getPerspectiveTransform(corners, dst)
    warped = cv2.warpPerspective(frame, H, (warp_w, warp_h))

    return warped, H


# ==========================================================
# PROCESAMIENTO DE COLOR
# ==========================================================
def process_colors(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_orange = clean_mask(cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE))
    mask_white = clean_mask(cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE))
    mask_blue = clean_mask(cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE))

    orange_obj = get_largest_object(mask_orange, MIN_OBJECT_AREA)
    white_obj = get_largest_object(mask_white, MIN_OBJECT_AREA)
    blue_obj = get_largest_object(mask_blue, MIN_OBJECT_AREA)

    return {
        "mask_orange": mask_orange,
        "mask_white": mask_white,
        "mask_blue": mask_blue,
        "orange_object": orange_obj,
        "white_object": white_obj,
        "blue_object": blue_obj,
    }


def draw_object_overlay(frame, obj, label, color_bgr):
    if obj is None:
        return frame

    out = frame.copy()
    x, y, w, h = obj["bbox"]
    cx, cy = obj["center"]
    area = obj["area"]

    cv2.rectangle(out, (x, y), (x + w, y + h), color_bgr, 2)
    cv2.circle(out, (cx, cy), 5, color_bgr, -1)
    cv2.putText(out, f"{label}", (x, y - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2)
    cv2.putText(out, f"({cx}, {cy}) A={int(area)}", (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_bgr, 2)

    return out


def build_annotated_frame(frame, workspace, color_data):
    annotated = frame.copy()

    annotated = draw_workspace_overlay(annotated, workspace)

    annotated = draw_object_overlay(annotated, color_data["orange_object"], "Orange", (0, 165, 255))
    annotated = draw_object_overlay(annotated, color_data["white_object"], "White", (255, 255, 255))
    annotated = draw_object_overlay(annotated, color_data["blue_object"], "Blue", (255, 0, 0))

    return annotated


# ==========================================================
# MAIN
# ==========================================================
def main():
    cap = open_camera(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)

    if cap is None:
        print("Error: no se pudo abrir la cámara.")
        return

    print("Cámara abierta correctamente.")
    print("Detectando workspace y objetos...")
    if SHOW_WINDOWS:
        print("Presiona 'q' para salir.")

    start_time = time.time()
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al leer frame.")
            break

        workspace, dark_mask = detect_workspace(frame)
        color_data = process_colors(frame)
        annotated = build_annotated_frame(frame, workspace, color_data)
        warped, H = warp_workspace(frame, workspace)

        frame_count += 1
        if frame_count % 30 == 0:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            print(f"FPS: {fps:.2f}")

            if workspace is not None:
                corners = workspace["corners"]
                print("Workspace corners (TL, TR, BR, BL):")
                print(np.round(corners, 1))
            else:
                print("Workspace no detectado.")

            print("-----")

        if SHOW_WINDOWS:
            cv2.imshow("Camera Feed", frame)
            cv2.imshow("Workspace Mask", dark_mask)
            cv2.imshow("Annotated Feed", annotated)

            if warped is not None:
                cv2.imshow("Warped Workspace", warped)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if SHOW_WINDOWS:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()