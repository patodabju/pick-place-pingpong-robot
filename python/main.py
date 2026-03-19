from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI

ui = WebUI()

print("Iniciando prueba de livestream web...")
print("Abre en tu navegador: http://<board-name>.local:7000")

App.run()