import json
import os
import threading
import time
import tkinter as tk
from tkinter import messagebox
from websocket import WebSocketApp
from obswebsocket import obsws, requests

# =====================================================================
#                      ⚙️ CONFIGURACIÓN FIJA
# =====================================================================
OBS_HOST = "localhost"
OBS_PORT = 4455
ACT_WS_URL = "ws://localhost:10501/ws"
CONFIG_FILE = "C:\\bos pruebas\\config_grabador.json"
# =====================================================================

class GrabadorIntuitivoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FFXIV Auto-Recorder")
        self.root.geometry("380x360") # Expandido un poco para la contraseña
        self.root.resizable(False, False)
        self.root.configure(bg="#1E1E1E")
        
        self.obs_client = None
        self.en_combate = False
        self.corriendo = False
        self.overlay = None
        self.lbl_overlay = None
        
        self.crear_interfaz()
        self.cargar_contrasena_guardada()

    def crear_interfaz(self):
        # Título
        lbl_titulo = tk.Label(self.root, text="FFXIV PULL RECORDER", font=("Segoe UI", 14, "bold"), fg="#00FFFF", bg="#1E1E1E")
        lbl_titulo.pack(pady=10)
        
        # --- SECCIÓN DE CONTRASEÑA OBS ---
        panel_pass = tk.LabelFrame(self.root, text=" Configuración OBS ", fg="#A0A0A0", bg="#1E1E1E", font=("Segoe UI", 9), padx=10, pady=5)
        panel_pass.pack(padx=20, fill="x", pady=5)
        
        tk.Label(panel_pass, text="Contraseña:", font=("Segoe UI", 10), fg="#FFFFFF", bg="#1E1E1E").pack(side="left", padx=5)
        
        # Caja de texto para la contraseña (oculta los caracteres con asteriscos)
        self.txt_password = tk.Entry(panel_pass, font=("Segoe UI", 10), fg="#00FF00", bg="#2D2D2D", bd=1, relief="solid", show="*")
        self.txt_password.pack(side="left", fill="x", expand=True, padx=5)
        
        # Botón para mostrar/ocultar el texto de la contraseña
        self.btn_ver = tk.Button(panel_pass, text="👁️", font=("Segoe UI", 8), fg="#FFFFFF", bg="#3E3E3E", bd=0, command=self.alternar_visibilidad_pass, width=3)
        self.btn_ver.pack(side="right", padx=2)
        
        # --- PANEL DE ESTADOS ---
        panel_estado = tk.LabelFrame(self.root, text=" Estado del Sistema ", fg="#A0A0A0", bg="#1E1E1E", font=("Segoe UI", 9), padx=15, pady=8)
        panel_estado.pack(padx=20, fill="x", pady=5)
        
        tk.Label(panel_estado, text="OBS Studio:", font=("Segoe UI", 10), fg="#FFFFFF", bg="#1E1E1E").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_obs_status = tk.Label(panel_estado, text="🔴 DESCONECTADO", font=("Segoe UI", 10, "bold"), fg="#FF5555", bg="#1E1E1E")
        self.lbl_obs_status.grid(row=0, column=1, sticky="w", padx=10)
        
        tk.Label(panel_estado, text="ACT (Overlay):", font=("Segoe UI", 10), fg="#FFFFFF", bg="#1E1E1E").grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_act_status = tk.Label(panel_estado, text="🔴 DESCONECTADO", font=("Segoe UI", 10, "bold"), fg="#FF5555", bg="#1E1E1E")
        self.lbl_act_status.grid(row=1, column=1, sticky="w", padx=10)
        
        tk.Label(panel_estado, text="Estado Raid:", font=("Segoe UI", 10), fg="#FFFFFF", bg="#1E1E1E").grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_game_status = tk.Label(panel_estado, text="💤 Fuera de combate", font=("Segoe UI", 10, "bold"), fg="#888888", bg="#1E1E1E")
        self.lbl_game_status.grid(row=2, column=1, sticky="w", padx=10)
        
        # --- BOTÓN DE ACCIÓN ---
        self.btn_accion = tk.Button(self.root, text="▶️ ENCIENDE EL GRABADOR", font=("Segoe UI", 11, "bold"), fg="#FFFFFF", bg="#28a745", activebackground="#218838", activeforeground="white", command=self.alternar_sistema)
        self.btn_accion.pack(pady=15, padx=20, fill="x")
        
        lbl_pie = tk.Label(self.root, text="Cierra la ventana para apagar todo.", font=("Segoe UI", 8, "italic"), fg="#555555", bg="#1E1E1E")
        lbl_pie.pack(side="bottom", pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_todo)

    def alternar_visibilidad_pass(self):
        """Muestra u oculta la contraseña al presionar el ojo"""
        if self.txt_password.cget("show") == "*":
            self.txt_password.config(show="")
        else:
            self.txt_password.config(show="*")

    def cargar_contrasena_guardada(self):
        """Carga la última contraseña usada desde un archivo JSON para que no la reescribas"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.txt_password.insert(0, data.get("obs_password", ""))
            except:
                pass

    def guardar_contrasena_actual(self):
        """Guarda de forma interna la contraseña que pusiste en la caja"""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, "w") as f:
                json.dump({"obs_password": self.txt_password.get()}, f)
        except:
            pass

    def crear_overlay(self):
        if self.overlay: return
        self.overlay = tk.Toplevel(self.root)
        self.overlay.title("FFXIV Recorder Overlay")
        self.overlay.geometry("160x30+10+40") 
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.configure(bg="#111111")
        self.overlay.attributes("-alpha", 0.8)

        self.lbl_overlay = tk.Label(self.overlay, text="⏱️ ESPERANDO PULL", font=("Segoe UI", 9, "bold"), fg="#888888", bg="#111111")
        self.lbl_overlay.pack(expand=True, fill="both")
        
        self.lbl_overlay.bind("<Button-1>", self.iniciar_arrastre)
        self.lbl_overlay.bind("<B1-Motion>", self.arrastrando)

    def iniciar_arrastre(self, event):
        self.x_offset = event.x
        self.y_offset = event.y

    def arrastrando(self, event):
        x = self.overlay.winfo_x() + event.x - self.x_offset
        y = self.overlay.winfo_y() + event.y - self.y_offset
        self.overlay.geometry(f"+{x}+{y}")

    def destruir_overlay(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            self.lbl_overlay = None

    def actualizar_estados_visuales(self, texto_panel, texto_overlay, color_fg):
        self.lbl_game_status.config(text=texto_panel, fg=color_fg)
        if self.lbl_overlay:
            self.lbl_overlay.config(text=texto_overlay, fg=color_fg)

    def alternar_sistema(self):
        if not self.corriendo:
            # Validar que no esté vacía
            if not self.txt_password.get().strip():
                messagebox.showwarning("Falta Contraseña", "Por favor, escribe o pega la contraseña de tu OBS primero.")
                return
                
            self.corriendo = True
            self.guardar_contrasena_actual() # Guarda la clave para la próxima vez
            self.txt_password.config(state="disabled") # Bloquea la caja mientras corre
            self.btn_accion.config(text="⏹️ APAGAR SISTEMA", bg="#dc3545", activebackground="#c82333")
            self.crear_overlay()
            
            threading.Thread(target=self.conectar_obs, daemon=True).start()
            threading.Thread(target=self.conectar_act, daemon=True).start()
        else:
            self.apagar_motores()

    def conectar_obs(self):
        if not self.corriendo: return
        try:
            contrasena = self.txt_password.get()
            self.obs_client = obsws(OBS_HOST, OBS_PORT, contrasena)
            self.obs_client.connect()
            self.lbl_obs_status.config(text="🟢 CONECTADO", fg="#55FF55")
            self.obs_client.call(requests.StartReplayBuffer())
        except Exception:
            self.lbl_obs_status.config(text="❌ ERROR DE CONEXIÓN", fg="#FF5555")
            # Si la contraseña está mal, apaga el sistema para corregirla
            self.root.after(500, self.apagar_motores)
            messagebox.showerror("Error OBS", "No se pudo conectar a OBS. Revisa si la contraseña es la correcta.")

    def conectar_act(self):
        if not self.corriendo: return
        
        def on_message(ws, message):
            if not self.corriendo: return
            try:
                data = json.loads(message)
                if data.get("type") == "CombatData" or "combatKey" in message:
                    combate_activo = str(data.get("isActive")).lower() == "true"
                    
                    if combate_activo and not self.en_combate:
                        self.en_combate = True
                        self.actualizar_estados_visuales("⚔️ ¡EN COMBATE (Grabando)!", "🔴 GRABANDO COMBATE", "#00FFFF")
                    elif not combate_activo and self.en_combate:
                        self.en_combate = False
                        self.actualizar_estados_visuales("💀 Wipe / Fin de pelea", "💾 SALVANDO CLIP...", "#FFA500")
                        self.guardar_repeticion_obs()
                        self.root.after(4000, lambda: self.actualizar_estados_visuales("💤 Esperando pull...", "⏱️ ESPERANDO PULL", "#888888") if not self.en_combate else None)
            except Exception:
                pass

        def on_close(ws, close_status_code, close_msg):
            if self.corriendo:
                self.lbl_act_status.config(text="🔄 RECONECTANDO ACT...", fg="#FFA500")
                if self.lbl_overlay: self.lbl_overlay.config(text="🔄 RECONECTANDO...", fg="#FFA500")
                time.sleep(4)
                if self.corriendo: self.conectar_act()

        def on_open(ws):
            self.lbl_act_status.config(text="🟢 CONECTADO", fg="#55FF55")
            self.actualizar_estados_visuales("💤 Esperando pull...", "⏱️ ESPERANDO PULL", "#888888")
            
            msg_1 = {"type": "subscribe", "id": "python-recorder", "events": ["CombatData"]}
            msg_2 = {"call": "subscribe", "events": ["CombatData"]}
            ws.send(json.dumps(msg_1))
            ws.send(json.dumps(msg_2))

        ws_act = WebSocketApp(ACT_WS_URL, on_open=on_open, on_message=on_message, on_close=on_close)
        ws_act.run_forever()

    def guardar_repeticion_obs(self):
        if self.obs_client and self.corriendo:
            try:
                self.obs_client.call(requests.SaveReplayBuffer())
            except Exception:
                pass

    def apagar_motores(self):
        self.corriendo = False
        self.en_combate = False
        if self.obs_client:
            try:
                self.obs_client.call(requests.StopReplayBuffer())
                self.obs_client.disconnect()
            except Exception:
                pass
        self.obs_client = None
        self.txt_password.config(state="normal") # Desbloquea la caja para poder editarla
        self.lbl_obs_status.config(text="🔴 DESCONECTADO", fg="#FF5555")
        self.lbl_act_status.config(text="🔴 DESCONECTADO", fg="#FF5555")
        self.lbl_game_status.config(text="💤 Fuera de combate", fg="#888888")
        self.btn_accion.config(text="▶️ ENCIENDE EL GRABADOR", bg="#28a745", activebackground="#218838")
        self.destruir_overlay()

    def cerrar_todo(self):
        self.apagar_motores()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GrabadorIntuitivoGUI(root)
    root.mainloop()