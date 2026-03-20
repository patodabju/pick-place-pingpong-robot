import tkinter as tk
from tkinter import ttk
import serial
import time

PORT = "COM7"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

root = tk.Tk()
root.title("Control Robot - Auto")

values = {
    "Base": 90,
    "A1": 90,
    "B": 90,
    "WristA": 90,
    "WristB": 90,
    "Gripper": 90
}

sliders = {}
value_labels = {}

last_send_time = 0

def send_angles(force=False):
    global last_send_time

    now = time.time()

    # evitar saturar serial
    if not force and (now - last_send_time < 0.05):
        return

    last_send_time = now

    cmd = f"{values['Base']} {values['A1']} {values['B']} {values['WristA']} {values['WristB']} {values['Gripper']}\n"
    ser.write(cmd.encode("utf-8"))
    print("Enviado:", cmd.strip())

def on_slider_change(name, val):
    values[name] = int(float(val))
    value_labels[name].config(text=str(values[name]))
    send_angles()

def build_slider(name, row):
    label_name = ttk.Label(root, text=name, width=10)
    label_name.grid(row=row, column=0, padx=10, pady=8)

    slider = ttk.Scale(
        root,
        from_=0,
        to=180,
        orient="horizontal",
        length=300,
        command=lambda val, n=name: on_slider_change(n, val)
    )
    slider.set(90)
    slider.grid(row=row, column=1, padx=10, pady=8)

    value_label = ttk.Label(root, text="90", width=5)
    value_label.grid(row=row, column=2)

    sliders[name] = slider
    value_labels[name] = value_label

def set_neutral():
    for name in values:
        values[name] = 90
        sliders[name].set(90)
        value_labels[name].config(text="90")

    send_angles(force=True)

row = 0
for name in ["Base", "A1", "B", "WristA", "WristB", "Gripper"]:
    build_slider(name, row)
    row += 1

neutral_btn = ttk.Button(root, text="Reset 90", command=set_neutral)
neutral_btn.grid(row=row, column=0, columnspan=3, pady=10)

root.mainloop()
ser.close()