from datetime import datetime, UTC
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection

ui = WebUI()
detection_stream = VideoObjectDetection()

def send_detections_to_ui(detections: dict):
    for key, value in detections.items():
        entry = {
            "content": key,
            "confidence": value,
            "timestamp": datetime.now(UTC).isoformat()
        }
        ui.send_message("detection", message=entry)

ui.on_message(
    "override_th",
    lambda sid, threshold: detection_stream.override_threshold(threshold)
)

detection_stream.on_detect_all(send_detections_to_ui)

print("App iniciada. Abre la interfaz web en la URL que te muestre App Lab.")
App.run()