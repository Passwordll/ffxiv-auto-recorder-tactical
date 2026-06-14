import json
import threading
import time
from websocket import WebSocketApp
from obswebsocket import obsws, requests

# =====================================================================
#                      ⚙️ CONFIGURACIÓN DEL SCRIPT
# =====================================================================
# Coloca aquí la misma contraseña que tienes en tus herramientas de OBS:
OBS_PASSWORD = "VvhKPLbN12juTkaR" 

OBS_HOST = "localhost"
OBS_PORT = 4455
ACT_WS_URL = "ws://localhost:10501/ws" # Puerto de tu Cactbot / OverlayPlugin
# =====================================================================

class FFXIVAutoRecorder:
    def __init__(self):
        self.obs_client = None
        self.en_combate = False
        
        # 1. Conectar a OBS Studio
        self.conectar_obs()
        
        # 2. Iniciar la escucha de ACT en segundo plano
        threading.Thread(target=self.conectar_act, daemon=True).start()

    def conectar_obs(self):
        try:
            self.obs_client = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
            self.obs_client.connect()
            print("✅ [OBS] ¡Conectado con éxito a OBS Studio!")
            
            # Encendemos el Buffer por si estaba apagado
            self.obs_client.call(requests.StartReplayBuffer())
            print("🎥 [OBS] Buffer de repetición asegurado y ENCENDIDO.")
        except Exception as e:
            print(f"❌ [OBS] Error al conectar a OBS. Detalles: {e}")

    def conectar_act(self):
        print("🔍 [ACT] Intentando conectar al servidor de OverlayPlugin...")
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                # Capturamos los datos de combate de ACT
                if data.get("type") == "CombatData":
                    combate_activo = data.get("isActive") == "true" or data.get("isActive") is True
                    
                    # SI EMPIEZA LA PELEA
                    if combate_activo and not self.en_combate:
                        self.en_combate = True
                        print("⚔️ [FFXIV] ¡Pull Iniciado! Tracking de combate activo...")
                    
                    # SI HAY WIPE O SE MUERE EL BOSS
                    elif not combate_activo and self.en_combate:
                        self.en_combate = False
                        print("💀 [FFXIV] Fin del combate detectado.")
                        self.guardar_repeticion_obs()
                        
            except Exception as e:
                pass

        def on_error(ws, error):
            pass

        def on_close(ws, close_status_code, close_msg):
            print("🔌 [ACT] Conexión perdida con ACT. Reintentando en 5 segundos...")
            time.sleep(5)
            self.conectar_act()

        def on_open(ws):
            print("🚀 [ACT] ¡Conectado al feed de FFXIV con éxito! Escuchando la raid...")
            # Nos suscribimos al canal de eventos de ACT
            subscribe_msg = {"type": "subscribe", "id": "python-recorder", "events": ["CombatData"]}
            ws.send(json.dumps(subscribe_msg))

        ws_act = WebSocketApp(ACT_WS_URL, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        ws_act.run_forever()

    def guardar_repeticion_obs(self):
        if self.obs_client:
            try:
                print("💾 [OBS] ¡Guardando video del último pull al disco duro...!")
                self.obs_client.call(requests.SaveReplayBuffer())
                print("⭐ [OBS] Clip guardado correctamente.")
            except Exception as e:
                print(f"❌ [OBS] No se pudo guardar el clip: {e}")

if __name__ == "__main__":
    print("=== FFXIV AUTO-RECORDER VIA ACT & OBS ===")
    print("Mantén esta ventana abierta mientras juegas.")
    print("==========================================")
    
    recorder = FFXIVAutoRecorder()
    
    # Mantener el programa despierto permanentemente
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nApagando grabador automático.")