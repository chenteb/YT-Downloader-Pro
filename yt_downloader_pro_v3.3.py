# =============================================================================
#  YT Downloader Pro v3.3
#  ---------------------------------------------------------------------------
#  Características:
#    - Interfaz gráfica amigable (Tkinter).
#    - Analizador integrado con detección de plataforma (Extractor).
#    - Descarga de Video en MP4 y Audio en MP3.
#    - Soporte para Playlists de YouTube.
#    - Historial de descargas persistente (historial.json).
#    - Verificación de integridad profunda (Plugin yt-dlp-CheckVideoIntegrity).
#    - Barra de progreso animada durante la verificación.
#    - Registro físico de verificaciones exitosas (registro_verificacion.txt).
#    - Ícono de ventana personalizado (app_icon.ico).
#
#  Plataformas Compatibles (Soportadas por yt-dlp):
#    - YouTube, Vimeo, Dailymotion, Twitch, Bilibili, NicoNico, Archive.org.
#    - Redes Sociales: Facebook, Twitter/X, Instagram, TikTok, Reddit, Tumblr.
#    - Noticias/TV: CNN, BBC, CBS, NBC, ABC, ESPN, Discovery.
#    - Música/Podcasts: SoundCloud, Bandcamp, Mixcloud, Acast.
#    - Cualquier otra página web con videos incrustados mediante el
#      "extractor genérico" (Generic).
#    - NOTA: Sitios con DRM (Netflix, Disney+, Hulu) NO están soportados.
#
#  Requisitos:
#    - Python 3.9+
#    - pip install yt-dlp
#    - pip install https://github.com/trainman261/yt-dlp-CheckVideoIntegrity/archive/master.zip
#    - FFmpeg en el PATH del sistema (para HD, MP3 y verificación).
# =============================================================================

import os
import sys
import json
import threading
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import yt_dlp
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Dependencia faltante", "Instala yt-dlp:\n\npip install yt-dlp")
    sys.exit(1)


# =============================================================================
# UTILIDAD PARA RUTAS DE RECURSOS (PyInstaller)
# =============================================================================
def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# =============================================================================
# CLASE PRINCIPAL
# =============================================================================
class YTDownloaderApp:
    HISTORIAL_FILE = "historial.json"
    LOG_VERIFICACION_FILE = "registro_verificacion.txt"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("YT Downloader Pro v3.3")
        self.root.geometry("700x650")
        self.root.resizable(False, False)

        # --- Ícono de la ventana -------------------------------------------
        icono_path = resource_path("app_icon.ico")
        try:
            if os.path.exists(icono_path):
                self.root.iconbitmap(icono_path)
        except Exception:
            pass

        # --- Variables de estado -------------------------------------------
        self.video_info = None
        self.formats_map = {}
        self.download_thread = None
        self.cancel_flag = False
        self.es_playlist = False

        # --- Cargar historial -----------------------------------------------
        self.historial = self._cargar_historial()

        # --- Construcción de la UI -----------------------------------------
        self._build_ui()
        self._check_ffmpeg()
        self._refrescar_historial_ui()

    # =========================================================================
    # CONSTRUCCIÓN DE LA INTERFAZ
    # =========================================================================
    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # --- 1. Entrada de URL ---------------------------------------------
        frame_url = ttk.LabelFrame(self.root, text="1. Enlace del Video (Cualquier Plataforma Compatible)")
        frame_url.pack(fill="x", **pad)

        self.url_var = tk.StringVar()
        entry = ttk.Entry(frame_url, textvariable=self.url_var)
        entry.pack(side="left", padx=8, pady=8, expand=True, fill="x")
        entry.bind("<Return>", lambda e: self._analizar_video())

        ttk.Button(frame_url, text="🔍 Analizar", command=self._analizar_video).pack(side="right", padx=8, pady=8)

        # --- 2. Información y Calidad --------------------------------------
        frame_info = ttk.LabelFrame(self.root, text="2. Información y Calidad")
        frame_info.pack(fill="x", **pad)

        self.lbl_titulo = ttk.Label(frame_info, text="Título: (sin analizar)", wraplength=650, justify="left")
        self.lbl_titulo.pack(anchor="w", padx=8, pady=(8, 2))

        # Etiqueta para mostrar la plataforma detectada (Youtube, Vimeo, Generic, etc.)
        self.lbl_plataforma = ttk.Label(frame_info, text="Plataforma: -", foreground="#0066cc")
        self.lbl_plataforma.pack(anchor="w", padx=8, pady=(0, 2))

        self.lbl_duracion = ttk.Label(frame_info, text="Duración / Elementos: -")
        self.lbl_duracion.pack(anchor="w", padx=8, pady=(0, 6))

        row_combo = ttk.Frame(frame_info)
        row_combo.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(row_combo, text="Calidad:").pack(side="left")
        self.combo_calidad = ttk.Combobox(row_combo, state="disabled", width=45)
        self.combo_calidad.pack(side="left", padx=8, fill="x", expand=True)

        # --- 3. Destino ----------------------------------------------------
        frame_dest = ttk.LabelFrame(self.root, text="3. Destino")
        frame_dest.pack(fill="x", **pad)

        row_carpeta = ttk.Frame(frame_dest)
        row_carpeta.pack(fill="x", padx=8, pady=4)
        ttk.Label(row_carpeta, text="Carpeta:", width=10).pack(side="left")
        self.carpeta_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        ttk.Entry(row_carpeta, textvariable=self.carpeta_var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(row_carpeta, text="📁 Elegir…", command=self._elegir_carpeta).pack(side="left")

        row_nombre = ttk.Frame(frame_dest)
        row_nombre.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(row_nombre, text="Nombre:", width=10).pack(side="left")
        self.nombre_var = tk.StringVar()
        ttk.Entry(row_nombre, textvariable=self.nombre_var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(row_nombre, text="(Playlist: nombre de carpeta)").pack(side="left")

        # --- 4. Descarga y Progreso ----------------------------------------
        frame_accion = ttk.LabelFrame(self.root, text="4. Descarga y Verificación")
        frame_accion.pack(fill="x", **pad)

        self.progress = ttk.Progressbar(frame_accion, orient="horizontal", mode="determinate", length=650)
        self.progress.pack(padx=10, pady=(10, 4), fill="x")

        self.lbl_estado = ttk.Label(frame_accion, text="Estado: esperando enlace…", foreground="#555")
        self.lbl_estado.pack(anchor="w", padx=10)

        frame_btns = ttk.Frame(frame_accion)
        frame_btns.pack(pady=10)
        
        self.btn_descargar = ttk.Button(frame_btns, text="⬇️ Descargar", command=self._iniciar_descarga, state="disabled")
        self.btn_descargar.pack(side="left", padx=5)
        
        self.btn_cancelar = ttk.Button(frame_btns, text="✖ Cancelar", command=self._cancelar_descarga, state="disabled")
        self.btn_cancelar.pack(side="left", padx=5)

        # --- 5. Historial --------------------------------------------------
        frame_hist = ttk.LabelFrame(self.root, text="5. Historial de Descargas")
        frame_hist.pack(fill="both", expand=True, **pad)

        cols = ("fecha", "titulo", "ruta")
        self.tree = ttk.Treeview(frame_hist, columns=cols, show="headings", height=6)
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("ruta", text="Ruta")
        self.tree.column("fecha", width=120)
        self.tree.column("titulo", width=300)
        self.tree.column("ruta", width=200)

        scroll = ttk.Scrollbar(frame_hist, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scroll.pack(side="right", fill="y", padx=(0, 8), pady=8)

        ttk.Button(frame_hist, text="🗑 Borrar Historial", command=self._borrar_historial).pack(pady=(0, 8))

    # =========================================================================
    # HISTORIAL
    # =========================================================================
    def _cargar_historial(self):
        if os.path.exists(self.HISTORIAL_FILE):
            try:
                with open(self.HISTORIAL_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _guardar_historial(self):
        try:
            with open(self.HISTORIAL_FILE, "w", encoding="utf-8") as f:
                json.dump(self.historial, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"No se pudo guardar historial: {e}")

    def _refrescar_historial_ui(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in reversed(self.historial):
            self.tree.insert("", "end", values=(item.get("fecha", ""), item.get("titulo", ""), item.get("ruta", "")))

    def _agregar_al_historial(self, titulo, ruta):
        entrada = {
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "titulo": titulo,
            "ruta": ruta,
        }
        self.historial.append(entrada)
        self._guardar_historial()
        self.root.after(0, self._refrescar_historial_ui)

    def _borrar_historial(self):
        if messagebox.askyesno("Confirmar", "¿Borrar todo el historial?"):
            self.historial = []
            self._guardar_historial()
            self._refrescar_historial_ui()

    # =========================================================================
    # ANÁLISIS (Soporta Video, Playlist y Detección de Plataforma)
    # =========================================================================
    def _analizar_video(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Falta enlace", "Pega un enlace de video.")
            return

        self._set_estado("Analizando…", "#0066cc")
        self.lbl_plataforma.config(text="Plataforma: Analizando...", foreground="#0066cc")
        self.combo_calidad.set("")
        self.combo_calidad["values"] = []
        self.combo_calidad.config(state="disabled")
        self.btn_descargar.config(state="disabled")

        threading.Thread(target=self._worker_analizar, args=(url,), daemon=True).start()

    def _worker_analizar(self, url):
        ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            # Extraemos el nombre de la plataforma detectada (Youtube, Vimeo, Generic, etc.)
            plataforma = info.get("extractor_key", info.get("extractor", "Desconocida"))

            # Detección de Playlist
            if "entries" in info:
                self.es_playlist = True
                titulo = info.get("title", "Playlist sin título")
                count = len([e for e in info.get("entries", []) if e])
                self.root.after(0, lambda: self._ui_tras_analisis_playlist(titulo, count, plataforma))
            else:
                self.es_playlist = False
                self.video_info = info
                formatos = self._extraer_formatos(info)
                titulo = info.get("title", "(sin título)")
                duracion = info.get("duration") or 0
                self.root.after(0, lambda: self._ui_tras_analisis_video(titulo, duracion, formatos, plataforma))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error de Compatibilidad", f"No se pudo analizar el enlace. Es posible que la plataforma no esté soportada o requiera actualización de yt-dlp:\n\n{e}"))
            self._set_estado("Error al analizar (Enlace no compatible).", "#cc0000")
            self.lbl_plataforma.config(text="Plataforma: No compatible", foreground="#cc0000")

    def _extraer_formatos(self, info):
        self.formats_map.clear()
        opciones = []
        video_formats = [f for f in info.get("formats", []) if f.get("vcodec") not in (None, "none")]

        mejores = {}
        for f in video_formats:
            altura = f.get("height") or 0
            tiene_audio = f.get("acodec") not in (None, "none")
            ext = f.get("ext", "")
            puntaje = (tiene_audio, ext == "mp4", f.get("tbr") or 0)
            if altura not in mejores or puntaje > mejores[altura][0]:
                mejores[altura] = (puntaje, f)

        for altura in sorted(mejores.keys(), reverse=True):
            if altura == 0:
                continue
            _, f = mejores[altura]
            etiqueta = f"{altura}p - {f.get('ext','').upper()}"
            self.formats_map[etiqueta] = f["format_id"]
            opciones.append(etiqueta)

        # Opciones universales
        opciones.insert(0, "🎯 Mejor calidad de Video (auto)")
        self.formats_map["🎯 Mejor calidad de Video (auto)"] = "bestvideo+bestaudio/best"
        
        opciones.append("🎵 Solo audio (MP3)")
        self.formats_map["🎵 Solo audio (MP3)"] = "audio_mp3"
        return opciones

    def _ui_tras_analisis_video(self, titulo, duracion, formatos, plataforma):
        self.lbl_titulo.config(text=f"Título: {titulo}")
        self.lbl_plataforma.config(text=f"Plataforma detectada: {plataforma} (Compatible ✓)", foreground="#006600")
        
        h, rem = divmod(duracion, 3600)
        m, s = divmod(rem, 60)
        self.lbl_duracion.config(text=f"Duración: {h:02d}:{m:02d}:{s:02d} | Tipo: Video individual")
        self.nombre_var.set(self._sanitizar_nombre(titulo)[:100])
        
        self.combo_calidad["values"] = formatos
        if formatos:
            self.combo_calidad.current(0)
        self.combo_calidad.config(state="readonly")
        self.btn_descargar.config(state="normal")
        self._set_estado("Listo. Elige calidad (o MP3) y descarga.", "#006600")

    def _ui_tras_analisis_playlist(self, titulo, count, plataforma):
        self.lbl_titulo.config(text=f"Playlist: {titulo}")
        self.lbl_plataforma.config(text=f"Plataforma detectada: {plataforma} (Compatible ✓)", foreground="#006600")
        self.lbl_duracion.config(text=f"Elementos: {count} | Tipo: Lista de reproducción")
        self.nombre_var.set(self._sanitizar_nombre(titulo)[:100])
        
        opciones = ["🎯 Mejor calidad de Video (auto)", "🎵 Solo audio (MP3)"]
        self.combo_calidad["values"] = opciones
        self.combo_calidad.current(0)
        self.combo_calidad.config(state="readonly")
        self.btn_descargar.config(state="normal")
        self._set_estado("Playlist detectada. Se descargarán todos los videos.", "#006600")

    # =========================================================================
    # DESCARGA Y VERIFICACIÓN
    # =========================================================================
    def _iniciar_descarga(self):
        calidad = self.combo_calidad.get()
        carpeta = self.carpeta_var.get().strip()
        if not os.path.isdir(carpeta):
            messagebox.showerror("Error", "La carpeta no existe.")
            return

        if self.es_playlist:
            url = self.url_var.get().strip()
            format_id = "audio_mp3" if calidad == "🎵 Solo audio (MP3)" else "bestvideo+bestaudio/best"
            nombre_base = self._sanitizar_nombre(self.nombre_var.get().strip()) or "Playlist"
            outtmpl = os.path.join(carpeta, nombre_base, "%(playlist_index)s - %(title)s.%(ext)s")
        else:
            if not self.video_info:
                return
            url = self.video_info["webpage_url"]
            format_id = self.formats_map.get(calidad, "bestvideo+bestaudio/best")
            nombre = self._sanitizar_nombre(self.nombre_var.get().strip()) or "video"
            outtmpl = os.path.join(carpeta, nombre + ".%(ext)s")

        self.btn_descargar.config(state="disabled")
        self.btn_cancelar.config(state="normal")
        self.cancel_flag = False
        self.progress["value"] = 0

        self.download_thread = threading.Thread(
            target=self._worker_descarga,
            args=(url, format_id, outtmpl, self.es_playlist),
            daemon=True
        )
        self.download_thread.start()

    def _worker_descarga(self, url, format_id, outtmpl, es_playlist):
        solo_audio = (format_id == "audio_mp3")
        ydl_format = "bestaudio/best" if solo_audio else format_id

        if solo_audio:
            outtmpl = outtmpl.replace(".%(ext)s", ".mp3")

        def hook(d):
            if self.cancel_flag:
                raise yt_dlp.utils.DownloadCancelled("Cancelado")
            
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                desc = d.get("downloaded_bytes", 0)
                if total > 0:
                    pct = desc / total * 100
                    self._set_progress(pct, determinate=True)
                    self._set_estado(f"Descargando… {pct:.1f}% ({desc/1e6:.1f}/{total/1e6:.1f} MB)", "#0066cc")
            elif d.get("status") == "finished":
                # La descarga terminó, ahora comienza el plugin de verificación (FFmpeg)
                self._set_progress(100, determinate=True)
                self._set_estado("Verificando integridad del archivo (esto puede tardar)...", "#cc6600")
                # Cambiamos la barra a modo indeterminado para mostrar actividad
                self.root.after(0, lambda: self.progress.config(mode="indeterminate"))
                self.root.after(0, lambda: self.progress.start(15))

        ydl_opts = {
            "format": ydl_format,
            "outtmpl": outtmpl,
            "progress_hooks": [hook],
            "quiet": True,
            "no_warnings": True,
            # Invocación del plugin de verificación de integridad
            "use_postprocessor": ["check_video_integrity"],
        }
        
        if solo_audio:
            ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        else:
            ydl_opts["merge_output_format"] = "mp4"
        
        if es_playlist:
            ydl_opts["ignoreerrors"] = True

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            
            # Registro de la descarga en el historial
            titulo_hist = info.get("title", "Desconocido")
            if es_playlist:
                titulo_hist = f"[Playlist] {titulo_hist}"
            
            ext_final = "mp3" if solo_audio else "mp4"
            ruta_historial = outtmpl.replace(".%(ext)s", f".{ext_final}")
            self._agregar_al_historial(titulo_hist, ruta_historial)
            
            # Registro físico de que la verificación fue exitosa
            self._escribir_log_exito(titulo_hist, ruta_historial)
            
            self.root.after(0, lambda: self._fin_descarga("¡Completado y verificado con éxito! ✓", "#006600", True))
            
        except yt_dlp.utils.DownloadCancelled:
            self.root.after(0, lambda: self._fin_descarga("Cancelado por el usuario.", "#cc0000", False))
        except Exception as e:
            # Si el plugin detecta corrupción en el archivo, el error cae aquí
            self.root.after(0, lambda: self._fin_descarga(f"Error o archivo corrupto:\n{e}", "#cc0000", False))

    def _fin_descarga(self, msg, color, exito):
        # Detenemos la animación de la barra indeterminada
        self.root.after(0, self.progress.stop)
        self.root.after(0, lambda: self.progress.config(mode="determinate"))
        
        # Ajustamos la barra al estado final
        if not exito:
            self.root.after(0, lambda: self.progress.config(value=0))
        else:
            self.root.after(0, lambda: self.progress.config(value=100))

        self._set_estado(msg, color)
        self.btn_descargar.config(state="normal")
        self.btn_cancelar.config(state="disabled")
        
        if exito:
            messagebox.showinfo("Proceso Exitoso", "El archivo se descargó y verificó correctamente.\nRevisa el historial.")
        else:
            messagebox.showerror("Error", "Hubo un problema con la descarga o la verificación del archivo.")

    def _cancelar_descarga(self):
        self.cancel_flag = True
        self._set_estado("Cancelando…", "#cc6600")

    # =========================================================================
    # UTILIDADES Y LOGS
    # =========================================================================
    def _escribir_log_exito(self, titulo, ruta):
        """Genera un archivo de texto con el registro de verificaciones exitosas."""
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{fecha}] ÉXITO: El archivo '{titulo}' pasó la verificación de integridad.\nRuta: {ruta}\n{'-'*60}\n"
        
        try:
            with open(self.LOG_VERIFICACION_FILE, "a", encoding="utf-8") as f:
                f.write(linea)
        except Exception as e:
            print(f"No se pudo escribir el log de verificación: {e}")

    def _check_ffmpeg(self):
        from shutil import which
        if which("ffmpeg"):
            self._set_estado("FFmpeg detectado ✓ Listo para trabajar.")
        else:
            self._set_estado("⚠ FFmpeg no encontrado (HD, MP3 y verificación fallarán).")
            messagebox.showwarning("FFmpeg", "FFmpeg no está en el PATH.\nDescárgalo de ffmpeg.org y agrégalo al PATH del sistema.")

    def _set_estado(self, txt, color="#555"):
        self.root.after(0, lambda: self.lbl_estado.config(text=f"Estado: {txt}", foreground=color))

    def _set_progress(self, val, determinate=True):
        """Actualiza la barra de progreso de forma segura."""
        def update():
            if determinate:
                self.progress.config(mode="determinate")
                self.progress["value"] = val
        self.root.after(0, update)

    def _elegir_carpeta(self):
        c = filedialog.askdirectory(initialdir=self.carpeta_var.get())
        if c: self.carpeta_var.set(c)

    @staticmethod
    def _sanitizar_nombre(n):
        for c in '<>:"/\\|?*': n = n.replace(c, "_")
        return n.strip() or "video"


# =============================================================================
# MAIN
# =============================================================================
def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass
    app = YTDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()