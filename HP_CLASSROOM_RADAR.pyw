import tkinter as tk
import psutil
import time
import threading
import os
import sys
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import urllib.request
import ctypes

VERSION_ACTUAL = "2.0"
URL_VERSION = "https://raw.githubusercontent.com/Powered-sp/HP_CLASSROOM_RADAR/refs/heads/main/version.txt"
URL_CODIGO = "https://raw.githubusercontent.com/Powered-sp/HP_CLASSROOM_RADAR/refs/heads/main/HP_CLASSROOM_RADAR.pyw"

class ClassroomRadar:
    def __init__(self):
        self.prev_status = False
        self.root = None
        self.blink_state = True
        self.running = True
        self.icon = None

    def check_for_updates(self):
        try:
            with urllib.request.urlopen(URL_VERSION, timeout=5) as response:
                version_remota = response.read().decode('utf-8').strip()
            
            if version_remota > VERSION_ACTUAL:
                with urllib.request.urlopen(URL_CODIGO, timeout=5) as response:
                    nuevo_codigo = response.read().decode('utf-8')
                
                ruta_actual = os.path.abspath(sys.argv[0])
                
                with open(ruta_actual, "w", encoding="utf-8") as f:
                    f.write(nuevo_codigo)
                
                os.startfile(ruta_actual)
                self.running = False
                if self.icon:
                    self.icon.stop()
                os._exit(0)
        except:
            pass

    def check_connection(self):
        if not self.running: return False
        try:
            for conn in psutil.net_connections(kind='tcp'):
                if conn.laddr.port == 5405 and conn.status == 'ESTABLISHED':
                    return True
        except:
            pass
        return False

    def create_dynamic_image(self, color):
        image = Image.new('RGB', (64, 64), (0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse([10, 10, 54, 54], fill=color)
        return image

    def update_icon_visual(self, connected):
        if self.icon:
            self.icon.icon = self.create_dynamic_image('red' if connected else 'green')

    def minimize_all_windows(self):
        try:
            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)
            ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
        except:
            pass

    def trigger_alert(self):
        if not self.running or self.root: return
        
        self.minimize_all_windows()
        time.sleep(0.1)
        
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True, '-topmost', True)
        self.root.configure(bg='black')
        self.root.config(cursor="arrow") 

        main_frame = tk.Frame(self.root, bg="black")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(main_frame, text="HP CLASSROOM RADAR", fg="deepskyblue", bg="black", font=("Arial", 25, "bold")).pack(pady=(0, 30))
        
        self.alert_top = tk.Label(main_frame, text="ATENCIÓN", fg="red", bg="black", font=("Arial Black", 70, "bold"))
        self.alert_top.pack()
        
        self.alert_bottom = tk.Label(main_frame, text="PROFESOR CONECTADO", fg="red", bg="black", font=("Arial Black", 50, "bold"))
        self.alert_bottom.pack(pady=(0, 40))
        
        tk.Button(main_frame, text="VOLVER AL ORDENADOR", command=self.close_alert, bg="#333333", fg="white", font=("Arial", 14, "bold"), padx=40, pady=20, relief="flat").pack()

        self.root.bind("<Escape>", lambda e: self.close_alert())
        self.blink()
        self.root.mainloop()

    def blink(self):
        if self.root and self.running:
            try:
                color = "red" if self.blink_state else "black"
                self.alert_top.config(fg=color)
                self.alert_bottom.config(fg=color)
                self.blink_state = not self.blink_state
                self.root.after(500, self.blink)
            except: pass

    def close_alert(self):
        if self.root:
            self.root.destroy()
            self.root = None

    def run_radar(self):
        self.check_for_updates()
        while self.running:
            is_connected = self.check_connection()
            
            if is_connected:
                if not self.prev_status:
                    self.prev_status = True
                    self.update_icon_visual(True)
                    self.trigger_alert()
            else:
                if self.prev_status:
                    self.prev_status = False
                    self.update_icon_visual(False)
            
            time.sleep(1)

radar = ClassroomRadar()

def on_quit(icon, item):
    radar.running = False
    radar.close_alert()
    icon.stop()
    os._exit(0)

try:
    initial_img = radar.create_dynamic_image('green')
    
    menu_radar = pystray.Menu(
        item('Cerrar Radar', on_quit),
        item(VERSION_ACTUAL, lambda: None, enabled=False)
    )
    
    icon_radar = pystray.Icon("Radar", initial_img, "HP CLASSROOM RADAR", menu_radar)
    radar.icon = icon_radar
    
    threading.Thread(target=radar.run_radar, daemon=True).start()
    
    icon_radar.run()
except Exception as e:
    with open("error_log.txt", "w") as f:
        f.write(str(e))
