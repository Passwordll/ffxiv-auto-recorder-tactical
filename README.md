# 🎮 FFXIV Auto Recorder Tactical

An automated, event-driven recording tool for Final Fantasy XIV that integrates Advanced Combat Tracker (ACT) events with OBS Studio via WebSockets. It automatically starts recording on encounter initialization and segments clips perfectly upon wipes or clears, eliminating the need to manage hours of continuous raid footage.

Una herramienta de grabación automatizada para Final Fantasy XIV que integra los eventos de Advanced Combat Tracker (ACT) con OBS Studio a través de WebSockets. Inicia la grabación automáticamente al empezar un pull y segmenta los clips de forma perfecta al ocurrir un wipe o clear, eliminando la necesidad de gestionar horas de metraje continuo.

---

## 💾 Downloads / Descargas
▶️ **[Download the latest release here / Descarga la última versión aquí](https://github.com/Passwordll/ffxiv-auto-recorder-tactical/releases)** 
*(Download the `.zip` file inside the Releases section / Descarga el archivo `.zip` dentro de la sección de Releases).*

---

## 🇪🇸 GUÍA DE CONFIGURACIÓN (ESPAÑOL)

Sigue estos 3 pasos rápidos para dejarlo configurado en tu PC (Solo se hace la primera vez):

### PASO 1: Activar el Servidor WebSockets en tu OBS
Para que el programa pueda darle las órdenes de "Grabar" y "Pausar" a tu OBS, necesitamos activar su control remoto:
1. Abre tu **OBS Studio**.
2. En el menú superior, haz clic en **Herramientas** ──► **Ajustes del servidor WebSockets**.
3. Asegúrate de marcar la casilla **Habilitar servidor WebSockets**.
4. El puerto por defecto debe ser `4455`.
5. Haz clic en **Generar contraseña** (o escribe una propia), dale a **Aplicar** y luego a **Aceptar**. *(¡No cierres OBS!)*.

### PASO 2: Iniciar el Grabador
1. Abre el archivo **`auto_grabador_gui.exe`** que viene dentro del ZIP.
2. En la sección **Configuración OBS**, escribe la contraseña que generaste en el paso anterior.
3. Dale al botón **Conectar**. Si todo está bien, verás un mensaje en verde que dice *"OBS Conectado"*.

### PASO 3: ¡A raidear!
* Deja el programa abierto en segundo plano (puedes minimizarlo).
* Entra al juego normalmente con tu **ACT** encendido como siempre.
* En cuanto el ACT detecte que entramos en combate, tu OBS empezará a grabar automáticamente. 
* Si morimos (*Wipe*), el video se cortará solo y quedará guardado en tu carpeta de videos de siempre de OBS.

---

## 🇺🇸 CONFIGURATION GUIDE (ENGLISH)

Follow these 3 quick steps to set it up on your PC (One-time setup only):

### STEP 1: Enable WebSockets Server in OBS
For the program to send "Record" and "Pause" commands to OBS, we need to enable remote control:
1. Open **OBS Studio**.
2. In the top menu, click on **Tools** ──► **WebSocket Server Settings**.
3. Make sure to check the **Enable WebSocket Server** box.
4. The default port should be `4455`.
5. Click **Generate Password** (or write your own), click **Apply**, and then **OK**. *(Keep OBS open!)*.

### STEP 2: Launch the Recorder
1. Open the **`auto_grabador_gui.exe`** file included in the ZIP.
2. In the **OBS Configuration** section, enter the password you generated in the previous step.
3. Click the **Connect** button. If successful, you will see a green message saying *"OBS Connected"*.

### STEP 3: Time to Raid!
* Leave the program running in the background (you can minimize it).
* Launch the game and make sure your **ACT** is running as usual.
* As soon as ACT detects we are in combat (Encounter Start), OBS will automatically start recording.
* If we die (*Wipe*), the recording will stop automatically and save the clip into your default OBS video folder.
