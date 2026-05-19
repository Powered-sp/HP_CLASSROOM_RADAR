import tkinter as tk
import time
import threading
import os
import sys
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import urllib.request

VERSION_ACTUAL = "1.2"
URL_VERSION = "https://raw.githubusercontent.com/Powered-sp/HP_CLASSROOM_RADAR/refs/heads/main/version.txt"
URL_CODIGO = "https://raw.githubusercontent.com/Powered-sp/HP_CLASSROOM_RADAR/refs/heads/main/radar.pyw"

class ClassroomRadar:
    def __init__(self):
        self.root = None
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

    def create_dynamic_image(self, color):
        image = Image.new('RGB', (64, 64), (0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse([10, 10, 54, 54], fill=color)
        return image

    def trigger_alert(self):
        if not self.running or self.root: return
        
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True, '-topmost', True)
        self.root.configure(bg='green')
        self.root.config(cursor="arrow") 

        self.root.bind("<Escape>", lambda e: self.close_alert())
        self.root.mainloop()

    def close_alert(self):
        if self.root:
            self.root.destroy()
            self.root = None

    def run_radar(self):
        self.check_for_updates()
        self.trigger_alert()
        while self.running:
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
        item('Cerrar Radar', on_quit)
    )
    
    icon_radar = pystray.Icon("Radar", initial_img, "HP CLASSROOM MANAGER RADAR", menu_radar)
    radar.icon = icon_radar
    
    threading.Thread(target=radar.run_radar, daemon=True).start()
    
    icon_radar.run()
except Exception as e:
    with open("error_log.txt", "w") as f:
        f.write(str(e))
