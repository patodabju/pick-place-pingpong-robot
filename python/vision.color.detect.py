import cv2
import numpy as np
import platform
import time


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================
SHOW_WINDOWS = True
CAMERA_INDEX = 0          # Laptop: 0 o 1 | UNO Q: el índice que ya encontraste
FRAME_WIDTH = 640
FRAME_HEIGHT = 360

# Dimensiones reales del workspace útil (dentro del tape)
WORKSPACE_WIDTH_CM = 36.4
WORKSPACE_HEIGHT_CM = 24.6

# Escala para la vista rectificada (px por cm)
WARP_SCALE = 20

# La máscara del workspace se erosiona hacia adentro
# para no detectar tape ni bordes internos
WORKSPACE_INSET_PX = 10

# Filtros geométricos de pelotas
MIN_OBJECT_AREA = 250
MAX_OBJECT_AREA = 50000
MIN_CIRCULARITY = 0.45
MIN_ASPECT_RATIO = 0.55
MAX_ASPECT_RATIO = 1.45

# --------------------------
# Rangos HSV
# --------------------------
# Naranja
LOWER_ORANGE = np.array([5, 100, 100])
UPPER_ORANGE = np.array([20, 255, 255])

# Azul baby-shower / cielo
LOWER_BLUE = np.array([85, 80, 80])
UPPER_BLUE = np.array([115, 255, 255])

# Blanco (ajuste conservador)
LOWER_WHITE = np.array([0, 0, 200])
UPPER_WHITE = np.array([179, 40, 255])


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

    # Intento de apagar AWB si la webcam lo soporta
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


# ==========================================================
# DETECCIÓN DEL WORKSPACE
# ==========================================================
def detect_workspace(frame):
    """
    Detecta el área útil como la mayor región oscura interior.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar zona negra / oscura
    _, dark_mask = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((7, 7), np.uint8)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, dark_mask

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    workspace_contour = None
    workspace_quad = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 10000:
            continue

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        if len(approx) == 4:
            workspace_contour = cnt
            workspace_quad = approx.reshape(4, 2)
            break

    # Si no encuentra 4 puntos limpios, usa rectángulo mínimo
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


def create_workspace_mask(frame_shape, workspace, inset_px=0):
    mask = np.zeros(frame_shape[:2], dtype=np.uint8)

    if workspace is None:
        return mask

    corners = workspace["corners"].astype(np.int32)
    cv2.fillPoly(mask, [corners], 255)

    if inset_px > 0:
        kernel = np.ones((inset_px, inset_px), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)

    return mask


def draw_workspace_overlay(frame, workspace):
    if workspace is None:
        return frame

    out = frame.copy()
    corners = workspace["corners"].astype(int)

    # Contorno
    cv2.polylines(out, [corners], isClosed=True, color=(0, 255, 0), thickness=2)

    # Etiquetas de esquinas
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
        return None, None, None, None

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

    return warped, H, warp_w, warp_h


# ==========================================================
# DETECCIÓN DE MÚLTIPLES OBJETOS
# ==========================================================
def get_all_objects(mask, min_area=250, max_area=50000,
                    min_circularity=0.45,
                    min_aspect_ratio=0.55,
                    max_aspect_ratio=1.45):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    objects = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area or area > max_area:
            continue

        peri = cv2.arcLength(cnt, True)
        if peri <= 0:
            continue

        circularity = 4.0 * np.pi * area / (peri * peri)

        x, y, w, h = cv2.boundingRect(cnt)
        if h == 0:
            continue

        aspect_ratio = w / h

        if circularity < min_circularity:
            continue

        if not (min_aspect_ratio <= aspect_ratio <= max_aspect_ratio):
            continue

        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        objects.append({
            "contour": cnt,
            "area": area,
            "center": (cx, cy),
            "bbox": (x, y, w, h),
            "circularity": circularity,
            "aspect_ratio": aspect_ratio,
        })

    # Orden: de arriba hacia abajo y luego de izquierda a derecha
    objects = sorted(objects, key=lambda obj: (obj["center"][1], obj["center"][0]))

    return objects


def process_colors(frame, workspace_mask=None):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_orange = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)
    mask_white = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)
    mask_blue = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)

    # Limitar detección al workspace útil
    if workspace_mask is not None:
        mask_orange = cv2.bitwise_and(mask_orange, workspace_mask)
        mask_white = cv2.bitwise_and(mask_white, workspace_mask)
        mask_blue = cv2.bitwise_and(mask_blue, workspace_mask)

    mask_orange = clean_mask(mask_orange)
    mask_white = clean_mask(mask_white)
    mask_blue = clean_mask(mask_blue)

    orange_objects = get_all_objects(
        mask_orange,
        MIN_OBJECT_AREA,
        MAX_OBJECT_AREA,
        MIN_CIRCULARITY,
        MIN_ASPECT_RATIO,
        MAX_ASPECT_RATIO
    )

    white_objects = get_all_objects(
        mask_white,
        MIN_OBJECT_AREA,
        MAX_OBJECT_AREA,
        MIN_CIRCULARITY,
        MIN_ASPECT_RATIO,
        MAX_ASPECT_RATIO
    )

    blue_objects = get_all_objects(
        mask_blue,
        MIN_OBJECT_AREA,
        MAX_OBJECT_AREA,
        MIN_CIRCULARITY,
        MIN_ASPECT_RATIO,
        MAX_ASPECT_RATIO
    )

    return {
        "mask_orange": mask_orange,
        "mask_white": mask_white,
        "mask_blue": mask_blue,
        "orange_objects": orange_objects,
        "white_objects": white_objects,
        "blue_objects": blue_objects,
    }


# ==========================================================
# CONVERSIÓN PIXEL -> COORDENADAS REALES
# ==========================================================
def pixel_to_workspace_cm(point_xy, H, warp_h):
    """
    Convierte un punto del frame original a coordenadas reales del workspace.
    Origen del workspace: esquina inferior izquierda.
    X crece hacia la derecha.
    Y crece hacia arriba.
    """
    if H is None or warp_h is None:
        return None

    pt = np.array([[[point_xy[0], point_xy[1]]]], dtype=np.float32)
    warped_pt = cv2.perspectiveTransform(pt, H)[0][0]

    x_px = warped_pt[0]
    y_px = warped_pt[1]

    x_cm = x_px / WARP_SCALE
    y_cm = (warp_h - y_px) / WARP_SCALE

    return (float(x_cm), float(y_cm))


def attach_workspace_coordinates(objects, H, warp_h):
    enriched = []

    for obj in objects:
        obj_copy = obj.copy()
        coords_cm = pixel_to_workspace_cm(obj["center"], H, warp_h)

        if coords_cm is not None:
            obj_copy["workspace_cm"] = coords_cm
        else:
            obj_copy["workspace_cm"] = None

        enriched.append(obj_copy)

    return enriched


# ==========================================================
# DIBUJO DE OBJETOS
# ==========================================================
def draw_objects_overlay(frame, objects, label_prefix, color_bgr):
    out = frame.copy()

    for idx, obj in enumerate(objects, start=1):
        x, y, w, h = obj["bbox"]
        cx, cy = obj["center"]
        area = obj["area"]

        cv2.rectangle(out, (x, y), (x + w, y + h), color_bgr, 2)
        cv2.circle(out, (cx, cy), 5, color_bgr, -1)

        title = f"{label_prefix}{idx}"
        cv2.putText(out, title, (x, y - 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_bgr, 2)

        if obj.get("workspace_cm") is not None:
            x_cm, y_cm = obj["workspace_cm"]
            subtitle = f"px=({cx},{cy}) cm=({x_cm:.1f},{y_cm:.1f})"
        else:
            subtitle = f"px=({cx},{cy}) A={int(area)}"

        cv2.putText(out, subtitle, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color_bgr, 2)

    return out


def build_annotated_frame(frame, workspace, color_data):
    annotated = frame.copy()

    annotated = draw_workspace_overlay(annotated, workspace)

    annotated = draw_objects_overlay(annotated, color_data["orange_objects"], "Orange_", (0, 165, 255))
    annotated = draw_objects_overlay(annotated, color_data["white_objects"], "White_", (255, 255, 255))
    annotated = draw_objects_overlay(annotated, color_data["blue_objects"], "Blue_", (255, 0, 0))

    return annotated


# ==========================================================
# DEBUG DE CONSOLA
# ==========================================================
def print_object_list(title, objects):
    print(f"{title}: {len(objects)} detectado(s)")
    for i, obj in enumerate(objects, start=1):
        cx, cy = obj["center"]
        area = obj["area"]

        if obj.get("workspace_cm") is not None:
            x_cm, y_cm = obj["workspace_cm"]
            print(f"  {title}_{i}: px=({cx},{cy}) cm=({x_cm:.2f},{y_cm:.2f}) area={area:.1f}")
        else:
            print(f"  {title}_{i}: px=({cx},{cy}) area={area:.1f}")


# ==========================================================
# MAIN
# ==========================================================
def main():
    cap = open_camera(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)

    if cap is None:
        print("Error: no se pudo abrir la cámara.")
        return

    print("Cámara abierta correctamente.")
    print("Detectando workspace y todas las pelotas...")
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
        workspace_mask = create_workspace_mask(frame.shape, workspace, inset_px=WORKSPACE_INSET_PX)
        warped, H, warp_w, warp_h = warp_workspace(frame, workspace)

        color_data = process_colors(frame, workspace_mask)

        # Convertir a coordenadas reales
        color_data["orange_objects"] = attach_workspace_coordinates(color_data["orange_objects"], H, warp_h)
        color_data["white_objects"] = attach_workspace_coordinates(color_data["white_objects"], H, warp_h)
        color_data["blue_objects"] = attach_workspace_coordinates(color_data["blue_objects"], H, warp_h)

        annotated = build_annotated_frame(frame, workspace, color_data)

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

            print_object_list("Orange", color_data["orange_objects"])
            print_object_list("Blue", color_data["blue_objects"])
            print_object_list("White", color_data["white_objects"])
            print("-----")

        if SHOW_WINDOWS:
            cv2.imshow("Camera Feed", frame)
            cv2.imshow("Workspace Mask", dark_mask)
            cv2.imshow("Workspace ROI Mask", workspace_mask)
            cv2.imshow("Orange Mask", color_data["mask_orange"])
            cv2.imshow("White Mask", color_data["mask_white"])
            cv2.imshow("Blue Mask", color_data["mask_blue"])
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