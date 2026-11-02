
# 🎬 YT Downloader Pro

Una aplicación de escritorio desarrollada en Python para Windows que permite descargar videos y audio de múltiples plataformas de forma sencilla, rápida y **verificando la integridad de cada archivo**.

**[Read in English](README.md)**

<!-- Opcional: Sube una captura de pantalla de tu app a GitHub y descomenta la siguiente línea -->
<!-- ![Demostración de la app](captura.png) -->

## ✨ Características

- **Interfaz Gráfica Amigable:** Fácil de usar, sin necesidad de comandos.
- **Multiplataforma:** Compatible con miles de sitios (YouTube, Vimeo, Facebook, Twitter, TikTok, etc.) gracias a `yt-dlp`.
- **Detección Automática:** El analizador integrado te indica de qué plataforma proviene el enlace.
- **Selección de Calidad:** Elige entre las diferentes resoluciones disponibles o descarga solo el audio.
- **Descarga de Audio (MP3):** Extrae la pista de audio en formato MP3 a 192 kbps.
- **Soporte para Playlists:** Descarga listas de reproducción completas (se guardan en una subcarpeta).
- **Verificación de Integridad:** Utiliza un plugin de `yt-dlp` y `FFmpeg` para asegurar que el archivo descargado no esté corrupto o incompleto.
- **Historial Persistente:** Lleva un registro de las descargas realizadas (`historial.json`).
- **Registro de Verificación:** Genera un archivo de texto (`registro_verificacion.txt`) confirmando que los archivos pasaron la prueba de integridad.

## 🚀 Requisitos Previos

1. **Python 3.9+** (solo si ejecutas el código fuente).
2. **FFmpeg** (Obligatorio): Necesario para descargar resoluciones altas (720p+), convertir a MP3 y realizar la verificación de integridad. 
   - Descárgalo de [ffmpeg.org](https://ffmpeg.org/download.html) y asegúrate de agregar la carpeta `bin` a las variables de entorno (PATH) de Windows.

## 🛠️ Instalación y Uso (Desde el código fuente)

1. Clona este repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/YT-Downloader-Pro.git
   cd YT-Downloader-Pro

2. Instala las dependencias:
   bash
   pip install -r requirements.txt

3. Ejecuta la aplicación:
   bash
   python yt_downloader_pro_v3.3.py

📦 Compilar como ejecutable (.exe)
Si deseas generar tu propio archivo ejecutable de Windows:

1. Instala PyInstaller:
   bash
   pip install pyinstaller

2. Ejecuta el siguiente comando en la raíz del proyecto:
   bash
   pyinstaller --onefile --noconsole --icon=app_icon.ico --add-data "app_icon.ico;." --name "YTDownloaderPro" yt_downloader_pro_v3.3.py

3. El ejecutable estará disponible en la carpeta dist/.

💡 Notas y Limitaciones Conocidas
   Títulos vacíos en algunas plataformas: Es posible que al analizar ciertos enlaces (por ejemplo, algunos Reels de Facebook o videos de Instagram), la plataforma no exponga la etiqueta del título. En estos casos, la app mostrará "(sin título)" en la interfaz, pero no hay problema: puedes escribir manualmente el nombre que desees en el campo "Nombre" antes de descargar y la aplicación lo respetará perfectamente.

   Sitios con DRM: Plataformas de streaming de pago como Netflix, Disney+ o Hulu utilizan protección DRM. Esta herramienta no puede descargar de esos sitios.

   Actualizaciones de plataformas: Si un sitio web deja de funcionar de repente, lo más probable es que haya cambiado su código. Actualizar yt-dlp (pip install -U yt-dlp) suele solucionarlo.

⚠️ Aviso Legal
   Esta herramienta está destinada a uso educativo y para descargar contenido propio o de dominio público. El usuario es responsable de cumplir con los Términos de Servicio de las plataformas (como YouTube) y las leyes de derechos de autor de su país. El desarrollador no se hace responsable del mal uso de este software.