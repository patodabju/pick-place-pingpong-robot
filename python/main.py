from arduino import App
from arduino.app_bricks.web_ui import WebUI

ui = WebUI()


def main():
    print("Iniciando prueba de livestream web...")
    print("Abre en tu navegador: http://<board-name>.local:7000")
    App.run()


if __name__ == "__main__":
    main()