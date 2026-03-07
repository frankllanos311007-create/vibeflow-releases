import customtkinter as ctk
import os
import threading
import yt_dlp
import json
import random
from tkinter import filedialog, messagebox
from pathlib import Path
import pygame
import time
from mutagen import File as MutagenFile
import urllib.request
import sys
import subprocess
import tempfile
import zipfile
import shutil
import webbrowser
from datetime import datetime
import re

try:
    import pywinstyles
    HAS_PYWIN = True
except ImportError:
    HAS_PYWIN = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# 🎨 PALETA DE COLORES
COLORS = {
    'bg_dark': '#1A0F1F',
    'bg_medium': '#2A1A2F',
    'bg_light': '#3A2540',
    'accent_primary': '#6198BD',
    'accent_secondary': '#616ABD',
    'accent_tertiary': '#8661BD',
    'accent_hover': '#4A7A9E',
    'text_primary': '#FEF9E7',
    'text_secondary': '#FAF0D7',
    'text_dim': '#E6D5B8',
    'success': '#48BB78',
    'error': '#F56565',
    'warning': '#F6AD55',
    'input_bg': '#2A2A3A',
    'input_border': '#3A3A4A'
}

# Inicializar pygame mixer
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
except pygame.error as e:
    print(f"Error inicializando pygame: {e}")
    pygame.mixer.init()

# ============================================
# SISTEMA DE ACTUALIZACIONES AUTOMÁTICAS
# ============================================

class ActualizadorAutomatico:
    """Sistema de actualizaciones automáticas"""
    
    def __init__(self, app, version_actual="1.0.3", repo_usuario="frankllanos311007-create", repo_nombre="vibeflow-releases"):
        self.app = app
        self.version_actual = version_actual
        self.repo_usuario = repo_usuario
        self.repo_nombre = repo_nombre
        self.url_version = f"https://raw.githubusercontent.com/{repo_usuario}/{repo_nombre}/main/version.json"
        self.url_descarga = f"https://github.com/{repo_usuario}/{repo_nombre}/releases/download/v{{version}}/reproductor.exe"
        
    def verificar(self, silencioso=True):
        try:
            print(f"🔍 Verificando actualizaciones... Versión actual: {self.version_actual}")
            req = urllib.request.Request(self.url_version, headers={'User-Agent': 'VibeFlow'})
            with urllib.request.urlopen(req, timeout=5) as respuesta:
                datos = json.loads(respuesta.read().decode())
                
            nueva_version = datos['version']
            cambios = datos.get('changelog', 'Mejoras generales')
            obligatoria = datos.get('mandatory', False)
            
            if self.comparar_versiones(nueva_version, self.version_actual) > 0:
                self.mostrar_notificacion(nueva_version, cambios, obligatoria)
                return True
            else:
                if not silencioso:
                    messagebox.showinfo("VibeFlow", "¡Tienes la última versión!")
                return False
                
        except Exception as e:
            if not silencioso:
                messagebox.showerror("Error", f"No se pudo verificar actualizaciones:\n{str(e)}")
        return False
    
    def comparar_versiones(self, v1, v2):
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            num1 = v1_parts[i] if i < len(v1_parts) else 0
            num2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if num1 > num2:
                return 1
            elif num1 < num2:
                return -1
        return 0
    
    def mostrar_notificacion(self, nueva_version, cambios, obligatoria):
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Actualización disponible")
        dialog.geometry("600x550")
        dialog.transient(self.app)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (self.app.winfo_width() - 600) // 2 + self.app.winfo_x()
        y = (self.app.winfo_height() - 550) // 2 + self.app.winfo_y()
        dialog.geometry(f"+{x}+{y}")
        
        # Título
        ctk.CTkLabel(
            dialog,
            text="🚀 ¡Nueva versión disponible!",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS['accent_primary']
        ).pack(pady=15)
        
        # Versiones
        frame_versiones = ctk.CTkFrame(dialog, fg_color=COLORS['bg_light'], corner_radius=10)
        frame_versiones.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            frame_versiones,
            text=f"Versión actual: {self.version_actual}",
            font=("Segoe UI", 14),
            text_color=COLORS['text_secondary']
        ).pack(pady=2)
        
        ctk.CTkLabel(
            frame_versiones,
            text=f"Versión nueva: {nueva_version}",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS['accent_primary']
        ).pack(pady=2)
        
        # Novedades
        frame_novedades = ctk.CTkFrame(dialog, fg_color=COLORS['bg_light'], corner_radius=10)
        frame_novedades.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            frame_novedades,
            text="📋 Novedades de esta versión:",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", padx=10, pady=5)
        
        texto_cambios = ctk.CTkTextbox(frame_novedades, height=120, fg_color="transparent")
        texto_cambios.pack(fill="both", expand=True, padx=10, pady=5)
        texto_cambios.insert("1.0", cambios)
        texto_cambios.configure(state="disabled")
        
        # Pasos para actualizar
        frame_pasos = ctk.CTkFrame(dialog, fg_color=COLORS['bg_light'], corner_radius=10)
        frame_pasos.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            frame_pasos,
            text="📌 Pasos para actualizar:",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS['accent_secondary']
        ).pack(anchor="w", padx=10, pady=5)
        
        pasos = [
            "1️⃣ Haz clic en 'DESCARGAR ACTUALIZACIÓN'",
            "2️⃣ Espera a que termine la descarga",
            "3️⃣ Cierra esta aplicación",
            "4️⃣ Ejecuta el archivo descargado",
            "5️⃣ Sigue las instrucciones del instalador"
        ]
        
        for paso in pasos:
            ctk.CTkLabel(
                frame_pasos,
                text=paso,
                font=("Segoe UI", 12),
                text_color=COLORS['text_secondary'],
                anchor="w"
            ).pack(anchor="w", padx=25, pady=1)
        
        # Barra de progreso (invisible al inicio)
        self.progress_descarga = ctk.CTkProgressBar(dialog, height=8)
        self.label_progreso = ctk.CTkLabel(dialog, text="", text_color=COLORS['text_secondary'])
        
        # Botones
        frame_botones = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_botones.pack(fill="x", padx=20, pady=15)
        
        # Botón descargar
        self.btn_descargar = ctk.CTkButton(
            frame_botones,
            text="⬇ DESCARGAR ACTUALIZACIÓN",
            command=lambda: self.descargar_actualizacion(nueva_version, dialog),
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'],
            height=45,
            width=220
        )
        self.btn_descargar.pack(side="left", padx=5)
        
        # Botón recordar después
        ctk.CTkButton(
            frame_botones,
            text="⏰ RECORDAR DESPUÉS",
            command=dialog.destroy,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS['accent_tertiary'],
            height=45,
            width=180,
            font=("Segoe UI", 13)
        ).pack(side="right", padx=5)

    def descargar_actualizacion(self, nueva_version, dialog):
        """Descarga el instalador a la carpeta Descargas"""
        try:
            # Nombre del instalador
            install_file = f"VibeFlow-Setup-v{nueva_version}.exe"
            url = f"https://github.com/{self.repo_usuario}/{self.repo_nombre}/releases/download/v{nueva_version}/{install_file}"
            
            # Carpeta de descargas del usuario
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            ruta_destino = os.path.join(downloads_path, install_file)
            
            # Mostrar progreso
            self.btn_descargar.configure(state="disabled", text="DESCARGANDO...")
            self.progress_descarga.pack(pady=5, padx=20, fill="x")
            self.label_progreso.pack()
            dialog.update()
            
            # Descarga
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as respuesta:
                total = int(respuesta.headers.get('Content-Length', 0))
                descargado = 0
                with open(ruta_destino, 'wb') as archivo:
                    while True:
                        chunk = respuesta.read(8192)
                        if not chunk:
                            break
                        archivo.write(chunk)
                        descargado += len(chunk)
                        if total > 0:
                            porc = descargado / total
                            self.progress_descarga.set(porc)
                            self.label_progreso.configure(
                                text=f"Descargando... {int(porc*100)}% completado"
                            )
                            dialog.update()
            
            # Descarga completada
            self.progress_descarga.set(1.0)
            self.label_progreso.configure(
                text="✅ ¡Descarga completada!",
                text_color=COLORS['success']
            )
            self.btn_descargar.configure(text="✓ DESCARGA COMPLETADA")
            
            # Mensaje de éxito
            messagebox.showinfo(
                "Descarga completada",
                f"El instalador se guardó en:\n{downloads_path}\n\n"
                "Pasos a seguir:\n"
                "1. Cierra esta aplicación\n"
                "2. Abre la carpeta de Descargas\n"
                "3. Ejecuta el archivo descargado\n"
                "4. Sigue el instalador"
            )
            
            # Preguntar si quiere abrir la carpeta
            if messagebox.askyesno("Abrir carpeta", "¿Quieres abrir la carpeta de Descargas ahora?"):
                os.startfile(downloads_path)
            
        except Exception as e:
            self.label_progreso.configure(
                text=f"❌ Error: No se pudo descargar. Verifica tu internet.",
                text_color=COLORS['error']
            )
            self.btn_descargar.configure(state="normal", text="⬇ INTENTAR DE NUEVO")
            messagebox.showerror(
                "Error de descarga",
                f"No se pudo descargar la actualización.\n\n"
                f"Puedes descargarla manualmente desde:\n"
                f"https://github.com/{self.repo_usuario}/{self.repo_nombre}/releases"
            )

# ============================================
# CLASES DE LA INTERFAZ
# ============================================

class HoverButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        self.hover_color = kwargs.get('hover_color', COLORS['accent_hover'])
        self.original_fg_color = kwargs.get('fg_color', COLORS['accent_primary'])
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def on_enter(self, e):
        self.configure(fg_color=self.hover_color)
        
    def on_leave(self, e):
        self.configure(fg_color=self.original_fg_color)
        
    def on_click(self, e):
        darker_color = self.darken_color(self.hover_color)
        self.configure(fg_color=darker_color)
        
    def on_release(self, e):
        self.configure(fg_color=self.hover_color)
        
    def darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f'#{r:02x}{g:02x}{b:02x}'

class SidebarButton(ctk.CTkButton):
    def __init__(self, master, text, icon, command=None, **kwargs):
        self.icon = icon
        self.text = text
        super().__init__(
            master,
            text=f"{icon}  {text}",
            anchor="w",
            height=45,
            fg_color="transparent",
            hover_color=COLORS['bg_light'],
            text_color=COLORS['text_secondary'],
            font=("Segoe UI", 14),
            corner_radius=8,
            command=command,
            **kwargs
        )
    
    def set_compact_mode(self, compact):
        if compact:
            self.configure(text=self.icon, width=50)
        else:
            self.configure(text=f"{self.icon}  {self.text}", width=None)

class SongCard(ctk.CTkFrame):
    def __init__(self, master, song_name, is_current=False, on_click=None, on_delete=None, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_light'] if is_current else COLORS['bg_medium'], 
                        corner_radius=15, height=80, **kwargs)
        self.pack(fill="x", pady=5, padx=10)
        self.pack_propagate(False)
        
        self.is_current = is_current
        self.on_click = on_click
        self.on_delete = on_delete
        self.song_name = song_name
        
        artist, title = self.parse_song_name(song_name)
        
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        title_label = ctk.CTkLabel(
            info_frame,
            text=title,
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        artist_label = ctk.CTkLabel(
            info_frame,
            text=f"🎤 {artist}",
            font=("Segoe UI", 13),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        artist_label.pack(anchor="w")
        
        # Botón eliminar
        self.btn_delete = ctk.CTkButton(
            self,
            text="🗑",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=COLORS['error'],
            text_color=COLORS['text_secondary'],
            font=("Segoe UI", 14),
            command=self.confirmar_eliminar
        )
        self.btn_delete.place(x=300, y=25)
        
        if is_current:
            self.play_icon = ctk.CTkLabel(
                self,
                text="▶",
                font=("Segoe UI", 24),
                text_color=COLORS['accent_primary']
            )
            self.play_icon.place(x=350, y=25)
        
        self.bind("<Button-1>", self.on_card_click)
        info_frame.bind("<Button-1>", self.on_card_click)
        title_label.bind("<Button-1>", self.on_card_click)
        artist_label.bind("<Button-1>", self.on_card_click)
        
    def parse_song_name(self, filename):
        name = os.path.splitext(filename)[0]
        separators = [' - ', ' – ', ' — ', ' by ', ' ft ', ' feat ']
        artist = "Artista desconocido"
        title = name
        
        for sep in separators:
            if sep in name:
                parts = name.split(sep, 1)
                artist = parts[0].strip()
                title = parts[1].strip()
                break
        
        return artist, title
    
    def on_card_click(self, event):
        if self.on_click:
            self.on_click()
    
    def confirmar_eliminar(self):
        if messagebox.askyesno("Eliminar", f"¿Eliminar {self.song_name}?"):
            if self.on_delete:
                self.on_delete()

class PlaylistList(ctk.CTkScrollableFrame):
    def __init__(self, master, on_song_select=None, on_song_delete=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_song_select = on_song_select
        self.on_song_delete = on_song_delete
        self.canciones = []
        self.current_idx = -1
        self.song_cards = []
        
    def update_songs(self, canciones, current_idx=-1):
        self.canciones = canciones
        self.current_idx = current_idx
        
        for widget in self.winfo_children():
            widget.destroy()
        self.song_cards = []
        
        for i, cancion in enumerate(canciones):
            song_card = SongCard(
                self,
                song_name=cancion,
                is_current=(i == current_idx),
                on_click=lambda idx=i: self.on_song_click(idx),
                on_delete=lambda idx=i: self.on_song_delete(idx) if self.on_song_delete else None
            )
            self.song_cards.append(song_card)
    
    def on_song_click(self, idx):
        if self.on_song_select:
            self.on_song_select(idx)
    
    def highlight_current(self, idx):
        self.current_idx = idx
        for i, card in enumerate(self.song_cards):
            if i == idx:
                card.configure(fg_color=COLORS['bg_light'])
                if not hasattr(card, 'play_icon'):
                    card.play_icon = ctk.CTkLabel(
                        card,
                        text="▶",
                        font=("Segoe UI", 24),
                        text_color=COLORS['accent_primary']
                    )
                    card.play_icon.place(x=350, y=25)
            else:
                card.configure(fg_color=COLORS['bg_medium'])
                if hasattr(card, 'play_icon'):
                    card.play_icon.destroy()
                    delattr(card, 'play_icon')

class VolumeControl(ctk.CTkFrame):
    def __init__(self, master, initial_volume=0.7, on_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.volume = initial_volume
        self.on_change = on_change
        self.muted = False
        self.prev_volume = initial_volume
        
        self.volume_icon = ctk.CTkLabel(
            self, text="🔊", font=("Segoe UI", 16), text_color=COLORS['text_secondary']
        )
        self.volume_icon.pack(side="left", padx=(0, 8))
        self.volume_icon.bind("<Button-1>", self.toggle_mute)
        
        self.volume_slider = ctk.CTkSlider(
            self, from_=0, to=1, command=self.on_slider_change, height=8,
            fg_color=COLORS['bg_light'], progress_color=COLORS['accent_primary'],
            button_color=COLORS['accent_secondary'], button_hover_color=COLORS['text_primary']
        )
        self.volume_slider.pack(side="left", fill="x", expand=True)
        self.volume_slider.set(initial_volume)
        
        self.volume_percent = ctk.CTkLabel(
            self, text=f"{int(initial_volume * 100)}%", font=("Segoe UI", 12),
            text_color=COLORS['text_secondary'], width=40
        )
        self.volume_percent.pack(side="left", padx=(5, 0))
        
    def on_slider_change(self, value):
        self.volume = float(value)
        self.volume_percent.configure(text=f"{int(self.volume * 100)}%")
        
        if self.volume == 0:
            self.volume_icon.configure(text="🔇")
        elif self.volume < 0.3:
            self.volume_icon.configure(text="🔈")
        elif self.volume < 0.7:
            self.volume_icon.configure(text="🔉")
        else:
            self.volume_icon.configure(text="🔊")
            
        if self.on_change:
            self.on_change(self.volume)
            
    def toggle_mute(self, event=None):
        if self.muted:
            self.volume = self.prev_volume
            self.volume_slider.set(self.volume)
            self.muted = False
        else:
            self.prev_volume = self.volume
            self.volume_slider.set(0)
            self.muted = True
        self.on_slider_change(self.volume_slider.get())

class ProgressBar(ctk.CTkFrame):
    def __init__(self, master, on_seek=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_seek = on_seek
        self.is_dragging = False
        self.current_time = 0
        self.total_time = 0
        
        self.time_current = ctk.CTkLabel(
            self, text="0:00", width=45, font=("Segoe UI", 13), text_color=COLORS['text_secondary']
        )
        self.time_current.pack(side="left")
        
        self.progress_slider = ctk.CTkSlider(
            self, from_=0, to=100, command=self.on_slider_drag, height=8,
            fg_color=COLORS['bg_light'], progress_color=COLORS['accent_primary'],
            button_color=COLORS['accent_secondary'], button_hover_color=COLORS['text_primary']
        )
        self.progress_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.progress_slider.set(0)
        
        self.progress_slider.bind("<ButtonPress-1>", self.on_drag_start)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_drag_end)
        
        self.time_total = ctk.CTkLabel(
            self, text="0:00", width=45, font=("Segoe UI", 13), text_color=COLORS['text_secondary']
        )
        self.time_total.pack(side="right")
        
    def on_drag_start(self, event):
        self.is_dragging = True
        
    def on_drag_end(self, event):
        self.is_dragging = False
        if self.on_seek:
            value = self.progress_slider.get()
            self.on_seek(value)
            
    def on_slider_drag(self, value):
        if self.is_dragging and self.total_time > 0:
            new_time = (float(value) / 100) * self.total_time
            self.time_current.configure(text=self.format_time(new_time))
        elif self.on_seek and not self.is_dragging:
            self.on_seek(value)
            
    def set_progress(self, current, total):
        self.current_time = current
        self.total_time = total
        self.time_current.configure(text=self.format_time(current))
        self.time_total.configure(text=self.format_time(total))
        
        if total > 0 and not self.is_dragging:
            progress = (current / total) * 100
            self.progress_slider.set(progress)
            
    def reset(self):
        self.current_time = 0
        self.progress_slider.set(0)
        self.time_current.configure(text="0:00")
            
    def format_time(self, seconds):
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

# ============================================
# CLASES DE DESCARGA PROFESIONAL
# ============================================

class DescargaItem(ctk.CTkFrame):
    """Item de descarga con control de pausa/reanudación"""
    def __init__(self, master, url, calidad="192", formato="mp3", tipo="audio", on_eliminar=None, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_light'], corner_radius=8, height=80, **kwargs)
        self.pack(fill="x", pady=2, padx=5)
        self.pack_propagate(False)
        
        self.url = url
        self.calidad = calidad
        self.formato = formato
        self.tipo = tipo
        self.on_eliminar = on_eliminar
        self.pausado = False
        self.proceso = None
        self.detener = False
        
        # Obtener título del video
        self.titulo = self.obtener_titulo(url)
        
        # Info
        ctk.CTkLabel(
            self, text=self.titulo, font=("Segoe UI", 12, "bold"),
            text_color=COLORS['text_primary'], anchor="w"
        ).place(x=10, y=5)
        
        self.label_info = ctk.CTkLabel(
            self, text=f"{'🎵' if tipo=='audio' else '🎬'} {formato.upper()} - {calidad}",
            font=("Segoe UI", 10), text_color=COLORS['text_secondary'], anchor="w"
        )
        self.label_info.place(x=10, y=25)
        
        self.label_estado = ctk.CTkLabel(
            self, text="⏳ Esperando...", font=("Segoe UI", 10),
            text_color=COLORS['warning'], anchor="w"
        )
        self.label_estado.place(x=10, y=40)
        
        self.progress = ctk.CTkProgressBar(
            self, height=6, fg_color=COLORS['bg_medium'],
            progress_color=COLORS['accent_primary'], width=300
        )
        self.progress.place(x=10, y=60)
        self.progress.set(0)
        
        # Botones
        self.btn_pausa = ctk.CTkButton(
            self, text="⏸", width=30, height=30, fg_color="transparent",
            hover_color=COLORS['accent_primary'], text_color=COLORS['text_secondary'],
            font=("Segoe UI", 14), command=self.toggle_pausa
        )
        self.btn_pausa.place(x=350, y=15)
        
        self.btn_eliminar = ctk.CTkButton(
            self, text="🗑", width=30, height=30, fg_color="transparent",
            hover_color=COLORS['error'], text_color=COLORS['text_secondary'],
            font=("Segoe UI", 14), command=self.eliminar
        )
        self.btn_eliminar.place(x=390, y=15)
        
        # Velocidad
        self.label_velocidad = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 9), text_color=COLORS['text_dim']
        )
        self.label_velocidad.place(x=350, y=50)
    
    def obtener_titulo(self, url):
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('title', 'Sin título')[:40] + ('...' if len(info.get('title', '')) > 40 else '')
        except:
            return "Video desconocido"
    
    def toggle_pausa(self):
        self.pausado = not self.pausado
        self.btn_pausa.configure(text="▶" if self.pausado else "⏸")
        self.label_estado.configure(
            text="⏸ Pausado" if self.pausado else "▶ Reanudando...",
            text_color=COLORS['warning'] if self.pausado else COLORS['accent_primary']
        )
    
    def eliminar(self):
        self.detener = True
        if self.on_eliminar:
            self.on_eliminar(self)
    
    def actualizar_progreso(self, d):
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                progress = d['downloaded_bytes'] / d['total_bytes']
                self.progress.set(progress)
                percent = int(progress * 100)
                
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024
                    self.label_velocidad.configure(text=f"{speed_mb:.1f} MB/s")
                
                eta = d.get('eta', 0)
                if eta and not self.pausado:
                    mins, secs = divmod(eta, 60)
                    self.label_estado.configure(
                        text=f"⬇ Descargando... {percent}% (faltan {mins}:{secs:02d})",
                        text_color=COLORS['success']
                    )
        
        elif d['status'] == 'finished':
            self.label_estado.configure(text="🔄 Procesando...", text_color=COLORS['accent_primary'])
            self.progress.set(1.0)
        
        elif d['status'] == 'error':
            self.label_estado.configure(text="❌ Error", text_color=COLORS['error'])
    
    def progreso_hook(self, d):
        if self.detener:
            raise Exception("Descarga cancelada")
        
        while self.pausado and not self.detener:
            time.sleep(0.5)
        
        self.actualizar_progreso(d)
    
    def descargar(self, ruta_carpeta):
        try:
            ydl_opts = {
                'format': 'bestaudio/best' if self.tipo == 'audio' else 'best',
                'outtmpl': os.path.join(ruta_carpeta, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progreso_hook],
                'quiet': True,
                'no_warnings': True,
            }
            
            if self.tipo == 'audio':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.formato,
                    'preferredquality': self.calidad,
                }]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            if not self.detener:
                self.label_estado.configure(text="✅ Completado", text_color=COLORS['success'])
                self.btn_pausa.destroy()
                self.btn_eliminar.configure(text="✓")
            
        except Exception as e:
            if not self.detener:
                self.label_estado.configure(text=f"❌ Error: {str(e)[:30]}", text_color=COLORS['error'])

class VentanaDescargasProfesional(ctk.CTkToplevel):
    """Ventana unificada de descargas"""
    def __init__(self, parent, ruta_carpeta):
        super().__init__(parent)
        
        self.parent = parent
        self.ruta_carpeta = ruta_carpeta
        self.descargas_activas = []
        
        self.title("VibeFlow - Reproductor Premium")
        self.geometry("800x600")
        self.configure(fg_color=COLORS['bg_medium'])
        self.transient(parent)
        
        # Centrar
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 800) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        # Tabs
        self.tabview = ctk.CTkTabview(self, fg_color=COLORS['bg_light'])
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_musica = self.tabview.add("🎵 Música")
        self.tab_videos = self.tabview.add("🎬 Videos")
        self.tab_cola = self.tabview.add("📋 Cola Activa")
        self.tab_archivos = self.tabview.add("📁 Archivos")
        
        # Configurar pestañas
        self.setup_musica()
        self.setup_videos()
        self.setup_cola()
        self.setup_archivos()
    
    def setup_musica(self):
        # URL
        frame_url = ctk.CTkFrame(self.tab_musica, fg_color="transparent")
        frame_url.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(frame_url, text="URL:", font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_url_musica = ctk.CTkEntry(
            frame_url, placeholder_text="https://youtube.com/watch?v=...",
            width=400, height=35, fg_color=COLORS['bg_light']
        )
        self.entry_url_musica.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            frame_url, text="📋 Pegar", width=60, height=35,
            fg_color=COLORS['bg_light'], hover_color=COLORS['accent_primary'],
            command=lambda: self.pegar_url(self.entry_url_musica)
        ).pack(side="left", padx=5)
        
        # Opciones
        frame_opciones = ctk.CTkFrame(self.tab_musica, fg_color="transparent")
        frame_opciones.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame_opciones, text="Calidad:").pack(side="left", padx=5)
        self.calidad_musica = ctk.CTkOptionMenu(
            frame_opciones, values=["128", "192", "320"], width=80
        )
        self.calidad_musica.pack(side="left", padx=5)
        self.calidad_musica.set("192")
        
        ctk.CTkLabel(frame_opciones, text="Formato:").pack(side="left", padx=5)
        self.formato_musica = ctk.CTkOptionMenu(
            frame_opciones, values=["mp3", "m4a", "wav"], width=80
        )
        self.formato_musica.pack(side="left", padx=5)
        self.formato_musica.set("mp3")
        
        ctk.CTkButton(
            frame_opciones, text="➕ Añadir a cola", width=120, height=35,
            fg_color=COLORS['accent_primary'], hover_color=COLORS['accent_hover'],
            command=self.anadir_musica
        ).pack(side="right", padx=5)
    
    def setup_videos(self):
        # URL
        frame_url = ctk.CTkFrame(self.tab_videos, fg_color="transparent")
        frame_url.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(frame_url, text="URL:", font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_url_video = ctk.CTkEntry(
            frame_url, placeholder_text="https://youtube.com/watch?v=...",
            width=400, height=35, fg_color=COLORS['bg_light']
        )
        self.entry_url_video.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            frame_url, text="📋 Pegar", width=60, height=35,
            fg_color=COLORS['bg_light'], hover_color=COLORS['accent_primary'],
            command=lambda: self.pegar_url(self.entry_url_video)
        ).pack(side="left", padx=5)
        
        # Opciones
        frame_opciones = ctk.CTkFrame(self.tab_videos, fg_color="transparent")
        frame_opciones.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame_opciones, text="Calidad:").pack(side="left", padx=5)
        self.calidad_video = ctk.CTkOptionMenu(
            frame_opciones, values=["720p", "1080p", "4K"], width=80
        )
        self.calidad_video.pack(side="left", padx=5)
        self.calidad_video.set("720p")
        
        ctk.CTkLabel(frame_opciones, text="Formato:").pack(side="left", padx=5)
        self.formato_video = ctk.CTkOptionMenu(
            frame_opciones, values=["mp4", "mkv", "webm"], width=80
        )
        self.formato_video.pack(side="left", padx=5)
        self.formato_video.set("mp4")
        
        ctk.CTkButton(
            frame_opciones, text="➕ Añadir a cola", width=120, height=35,
            fg_color=COLORS['accent_primary'], hover_color=COLORS['accent_hover'],
            command=self.anadir_video
        ).pack(side="right", padx=5)
    
    def setup_cola(self):
        self.frame_cola = ctk.CTkScrollableFrame(self.tab_cola, fg_color="transparent")
        self.frame_cola.pack(fill="both", expand=True, padx=5, pady=5)
        
        frame_botones = ctk.CTkFrame(self.tab_cola, fg_color="transparent")
        frame_botones.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            frame_botones, text="⏯ Iniciar todas", width=120,
            fg_color=COLORS['accent_secondary'], command=self.iniciar_todas
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            frame_botones, text="⏸ Pausar todas", width=120,
            fg_color=COLORS['warning'], command=self.pausar_todas
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            frame_botones, text="⏹ Detener todas", width=120,
            fg_color=COLORS['error'], command=self.detener_todas
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            frame_botones, text="🗑 Limpiar completadas", width=140,
            fg_color=COLORS['bg_light'], command=self.limpiar_completadas
        ).pack(side="right", padx=2)
    
    def setup_archivos(self):
        # Lista de archivos en la carpeta
        self.frame_archivos = ctk.CTkScrollableFrame(self.tab_archivos, fg_color="transparent")
        self.frame_archivos.pack(fill="both", expand=True, padx=5, pady=5)
        
        frame_botones = ctk.CTkFrame(self.tab_archivos, fg_color="transparent")
        frame_botones.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            frame_botones, text="🔄 Refrescar", width=100,
            fg_color=COLORS['bg_light'], command=self.cargar_archivos
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            frame_botones, text="📁 Abrir carpeta", width=120,
            fg_color=COLORS['accent_primary'], command=self.abrir_carpeta
        ).pack(side="right", padx=2)
        
        self.cargar_archivos()
    
    def cargar_archivos(self):
        for widget in self.frame_archivos.winfo_children():
            widget.destroy()
        
        if not os.path.exists(self.ruta_carpeta):
            return
        
        formatos = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.mp4', '.mkv', '.webm')
        archivos = []
        
        for archivo in os.listdir(self.ruta_carpeta):
            if archivo.lower().endswith(formatos):
                archivos.append(archivo)
        
        archivos.sort()
        
        for archivo in archivos:
            frame = ctk.CTkFrame(self.frame_archivos, fg_color=COLORS['bg_light'], height=40)
            frame.pack(fill="x", pady=1)
            frame.pack_propagate(False)
            
            ctk.CTkLabel(frame, text=archivo, anchor="w").pack(side="left", padx=10)
            
            ctk.CTkButton(
                frame, text="🗑", width=30, height=30,
                fg_color="transparent", hover_color=COLORS['error'],
                command=lambda f=archivo: self.eliminar_archivo(f)
            ).pack(side="right", padx=5)
    
    def eliminar_archivo(self, archivo):
        try:
            os.remove(os.path.join(self.ruta_carpeta, archivo))
            self.cargar_archivos()
            self.parent.cargar_canciones()
        except:
            pass
    
    def abrir_carpeta(self):
        if os.path.exists(self.ruta_carpeta):
            os.startfile(self.ruta_carpeta)
    
    def pegar_url(self, entry):
        try:
            url = self.clipboard_get()
            entry.delete(0, 'end')
            entry.insert(0, url)
        except:
            pass
    
    def anadir_musica(self):
        url = self.entry_url_musica.get().strip()
        if url:
            item = DescargaItem(
                self.frame_cola,
                url,
                calidad=self.calidad_musica.get(),
                formato=self.formato_musica.get(),
                tipo="audio",
                on_eliminar=self.eliminar_item
            )
            self.descargas_activas.append(item)
            self.entry_url_musica.delete(0, 'end')
    
    def anadir_video(self):
        url = self.entry_url_video.get().strip()
        if url:
            item = DescargaItem(
                self.frame_cola,
                url,
                calidad=self.calidad_video.get(),
                formato=self.formato_video.get(),
                tipo="video",
                on_eliminar=self.eliminar_item
            )
            self.descargas_activas.append(item)
            self.entry_url_video.delete(0, 'end')
    
    def eliminar_item(self, item):
        if item in self.descargas_activas:
            self.descargas_activas.remove(item)
            item.destroy()
    
    def iniciar_todas(self):
        for item in self.descargas_activas:
            if item.label_estado.cget("text") == "⏳ Esperando...":
                threading.Thread(target=item.descargar, args=(self.ruta_carpeta,), daemon=True).start()
    
    def pausar_todas(self):
        for item in self.descargas_activas:
            if not item.pausado:
                item.toggle_pausa()
    
    def detener_todas(self):
        for item in self.descargas_activas:
            item.detener = True
        self.descargas_activas.clear()
        for widget in self.frame_cola.winfo_children():
            widget.destroy()
    
    def limpiar_completadas(self):
        for item in self.descargas_activas[:]:
            if "✅" in item.label_estado.cget("text"):
                self.eliminar_item(item)

class VentanaBiblioteca(ctk.CTkToplevel):
    """Ventana de biblioteca con búsqueda automática por artista"""
    def __init__(self, parent, canciones, ruta_carpeta, on_reproducir, on_eliminar):
        super().__init__(parent)
        
        self.parent = parent
        self.canciones = canciones
        self.ruta_carpeta = ruta_carpeta
        self.on_reproducir = on_reproducir
        self.on_eliminar = on_eliminar
        
        self.title("📚 Biblioteca Musical")
        self.geometry("900x600")
        self.configure(fg_color=COLORS['bg_medium'])
        self.transient(parent)
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 900) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        # Buscador
        frame_buscar = ctk.CTkFrame(self, fg_color="transparent")
        frame_buscar.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(frame_buscar, text="🔍", font=("Segoe UI", 16)).pack(side="left", padx=5)
        
        self.entry_buscar = ctk.CTkEntry(
            frame_buscar, placeholder_text="Buscar artista o canción...",
            height=35, fg_color=COLORS['bg_light']
        )
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_buscar.bind("<KeyRelease>", self.filtrar)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Panel artistas
        frame_artistas = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_light'], width=300)
        frame_artistas.pack(side="left", fill="y", padx=(0, 10))
        frame_artistas.pack_propagate(False)
        
        ctk.CTkLabel(frame_artistas, text="🎤 Artistas", font=("Segoe UI", 16, "bold"),
                    text_color=COLORS['accent_secondary']).pack(pady=10)
        
        self.lista_artistas = ctk.CTkScrollableFrame(frame_artistas, fg_color="transparent")
        self.lista_artistas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Panel canciones
        frame_canciones = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_light'])
        frame_canciones.pack(side="right", fill="both", expand=True)
        
        ctk.CTkLabel(frame_canciones, text="🎵 Canciones", font=("Segoe UI", 16, "bold"),
                    text_color=COLORS['accent_secondary']).pack(pady=10)
        
        self.lista_canciones = ctk.CTkScrollableFrame(frame_canciones, fg_color="transparent")
        self.lista_canciones.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cargar datos
        self.procesar_canciones()
        self.cargar_artistas()
    
    def procesar_canciones(self):
        self.canciones_info = []
        for cancion in self.canciones:
            nombre = os.path.splitext(cancion)[0]
            artista = "Artista desconocido"
            
            separators = [' - ', ' – ', ' — ', ' by ', ' ft ', ' feat ']
            for sep in separators:
                if sep in nombre:
                    artista = nombre.split(sep, 1)[0].strip()
                    break
            
            self.canciones_info.append({
                'archivo': cancion,
                'artista': artista,
                'titulo': nombre,
                'ruta': os.path.join(self.ruta_carpeta, cancion)
            })
    
    def cargar_artistas(self, filtro=""):
        for widget in self.lista_artistas.winfo_children():
            widget.destroy()
        
        artistas = set()
        for info in self.canciones_info:
            if filtro.lower() in info['artista'].lower() or filtro.lower() in info['titulo'].lower():
                artistas.add(info['artista'])
        
        for artista in sorted(artistas):
            btn = ctk.CTkButton(
                self.lista_artistas,
                text=artista,
                anchor="w",
                fg_color="transparent",
                hover_color=COLORS['bg_medium'],
                text_color=COLORS['text_secondary'],
                command=lambda a=artista: self.mostrar_canciones(a)
            )
            btn.pack(fill="x", pady=1)
    
    def mostrar_canciones(self, artista):
        for widget in self.lista_canciones.winfo_children():
            widget.destroy()
        
        for info in self.canciones_info:
            if info['artista'] == artista:
                frame = ctk.CTkFrame(self.lista_canciones, fg_color=COLORS['bg_light'], height=40)
                frame.pack(fill="x", pady=1)
                frame.pack_propagate(False)
                
                ctk.CTkLabel(frame, text=info['titulo'], anchor="w").pack(side="left", padx=10)
                
                ctk.CTkButton(
                    frame, text="▶", width=30, height=30,
                    fg_color="transparent", hover_color=COLORS['accent_primary'],
                    command=lambda i=info: self.reproducir(i)
                ).pack(side="right", padx=2)
                
                ctk.CTkButton(
                    frame, text="🗑", width=30, height=30,
                    fg_color="transparent", hover_color=COLORS['error'],
                    command=lambda i=info: self.eliminar(i)
                ).pack(side="right", padx=2)
    
    def reproducir(self, info):
        idx = self.canciones.index(info['archivo'])
        self.on_reproducir(idx)
        self.destroy()
    
    def eliminar(self, info):
        if messagebox.askyesno("Eliminar", f"¿Eliminar {info['titulo']}?"):
            try:
                os.remove(info['ruta'])
                self.canciones.remove(info['archivo'])
                self.procesar_canciones()
                self.cargar_artistas()
                self.on_eliminar()
            except:
                pass
    
    def filtrar(self, event=None):
        texto = self.entry_buscar.get()
        self.cargar_artistas(texto)

class AnimatedSidebar(ctk.CTkFrame):
    def __init__(self, master, width_expanded=200, width_collapsed=50, on_logout=None, on_check_updates=None, **kwargs):
        super().__init__(master, width=width_expanded, **kwargs)
        
        self.width_expanded = width_expanded
        self.width_collapsed = width_collapsed
        self.is_expanded = True
        self.animation_running = False
        self.on_logout = on_logout
        self.on_check_updates = on_check_updates
        
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.toggle_btn = ctk.CTkButton(
            self.content_frame, text="◀", width=30, height=30,
            fg_color="transparent", hover_color=COLORS['bg_light'],
            text_color=COLORS['text_secondary'], font=("Segoe UI", 14),
            corner_radius=15, command=self.toggle_sidebar
        )
        self.toggle_btn.pack(anchor="ne", pady=5, padx=5)
        
        self.logo_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.logo_frame.pack(fill="x", pady=(0, 20))
        
        self.logo_label = ctk.CTkLabel(
            self.logo_frame, text="VibeFlow",
            font=("Segoe UI", 18, "bold"), text_color=COLORS['accent_primary']
        )
        self.logo_label.pack()
        
        self.nav_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.nav_frame.pack(fill="x", pady=10)
        
        self.bottom_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", pady=10)
        
        self.user_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.user_frame.pack(fill="x", pady=(0, 10))
        
        self.user_avatar = ctk.CTkLabel(
            self.user_frame, text="👤", font=("Segoe UI", 20), text_color=COLORS['text_secondary']
        )
        self.user_avatar.pack()
        
        self.user_name = ctk.CTkLabel(
            self.user_frame, text="Usuario", font=("Segoe UI", 11), text_color=COLORS['text_secondary']
        )
        self.user_name.pack()
        
        self.update_btn = SidebarButton(
            self.bottom_frame, text="Buscar actualizaciones", icon="🔄", command=self.check_updates
        )
        self.update_btn.pack(pady=2, fill="x")
        
        self.logout_btn = SidebarButton(
            self.bottom_frame, text="Cerrar Sesión", icon="🚪", command=self.logout
        )
        self.logout_btn.pack(pady=2, fill="x")
        
        self.nav_buttons = []
        
    def add_nav_button(self, text, icon, command):
        btn = SidebarButton(self.nav_frame, text=text, icon=icon, command=command)
        btn.pack(pady=2, fill="x")
        self.nav_buttons.append(btn)
        return btn
    
    def set_user_info(self, username):
        self.user_name.configure(text=username)
    
    def logout(self):
        if self.on_logout:
            self.on_logout()
    
    def check_updates(self):
        if self.on_check_updates:
            self.on_check_updates()
    
    def toggle_sidebar(self):
        if self.animation_running:
            return
        
        self.animation_running = True
        target_width = self.width_collapsed if self.is_expanded else self.width_expanded
        
        def animate():
            current_width = self.winfo_width()
            step = 10 if target_width > current_width else -10
            steps = abs(target_width - current_width) // 10
            
            def step_animation(count=0):
                if count < steps:
                    new_width = current_width + (step * (count + 1))
                    self.configure(width=new_width)
                    self.after(10, lambda: step_animation(count + 1))
                else:
                    self.configure(width=target_width)
                    self.is_expanded = not self.is_expanded
                    self.update_content_mode()
                    self.animation_running = False
                    self.toggle_btn.configure(text="▶" if not self.is_expanded else "◀")
            
            step_animation()
        
        animate()
    
    def update_content_mode(self):
        if self.is_expanded:
            self.logo_frame.pack(fill="x", pady=(0, 20))
            for btn in self.nav_buttons:
                btn.set_compact_mode(False)
            self.update_btn.set_compact_mode(False)
            self.logout_btn.set_compact_mode(False)
            self.user_frame.pack(fill="x", pady=(0, 10))
        else:
            self.logo_frame.pack_forget()
            for btn in self.nav_buttons:
                btn.set_compact_mode(True)
            self.update_btn.set_compact_mode(True)
            self.logout_btn.set_compact_mode(True)
            self.user_frame.pack_forget()

# ============================================
# CLASE PRINCIPAL VIBEFLOW
# ============================================

class VibeFlow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VibeFlow")
        self.geometry("1200x750")
        self.configure(fg_color=COLORS['bg_dark'])
        self.resizable(True, True)

        # Variables
        self.ruta_carpeta = ""
        self.canciones = []
        self.cancion_actual_idx = -1
        self.esta_reproduciendo = False
        self.duracion_actual = 0.0
        self.volumen = 0.7
        self.shuffle = False
        self.repeat = False
        self.usuario_actual = None
        self.descarga_en_progreso = False
        self.posicion_actual = 0
        self.pausado = False
        self.current_view = "reproductor"
        
        # Versión de la aplicación
        self.version_actual = "1.0.3"
        
        # Configuración de GitHub
        self.repo_usuario = "frankllanos311007-create"
        self.repo_nombre = "vibeflow-releases"
        
        # Inicializar actualizador
        self.actualizador = ActualizadorAutomatico(
            self, self.version_actual, self.repo_usuario, self.repo_nombre
        )

        # Configuración
        self.config_path = Path("vibeflow_config.json")
        
        self.cargar_configuracion()
        self.crear_login()

        if HAS_PYWIN:
            try:
                pywinstyles.apply_style(self, "mica")
            except:
                pass

    def cargar_configuracion(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.usuario_actual = config.get('usuario')
                    self.ruta_carpeta = config.get('ultima_carpeta', '')
                    self.volumen = config.get('volumen', 0.7)
            except:
                pass

    def guardar_configuracion(self):
        config = {
            'usuario': self.usuario_actual,
            'ultima_carpeta': self.ruta_carpeta,
            'volumen': self.volumen
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except:
            pass

    def crear_login(self):
        self.login_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'], corner_radius=30)
        self.login_frame.pack(expand=True, fill="both", padx=30, pady=30)

        center_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        center_frame.pack(expand=True)

        # Logo
        logo_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        logo_frame.pack(pady=(0, 10))

        colors = [COLORS['accent_primary'], COLORS['accent_secondary'], COLORS['accent_tertiary']]
        for color in colors:
            dot = ctk.CTkLabel(logo_frame, text="●", font=("Segoe UI", 40), text_color=color)
            dot.pack(side="left", padx=2)

        ctk.CTkLabel(
            center_frame, text="VibeFlow", font=("Segoe UI", 48, "bold"),
            text_color=COLORS['accent_primary']
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            center_frame, text="Tu música, tu flow", font=("Segoe UI", 16, "italic"),
            text_color=COLORS['text_secondary']
        ).pack(pady=(0, 40))

        input_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        input_frame.pack(pady=10)

        # Usuario
        user_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        user_frame.pack(pady=5)

        ctk.CTkLabel(user_frame, text="👤", font=("Segoe UI", 20), text_color=COLORS['accent_primary'], width=40).pack(side="left")

        self.username_entry = ctk.CTkEntry(
            user_frame, placeholder_text="Nombre de usuario", width=300, height=45,
            font=("Segoe UI", 14), fg_color=COLORS['input_bg'], border_color=COLORS['accent_primary'],
            border_width=2, corner_radius=10
        )
        self.username_entry.pack(side="left")

        # Contraseña
        pass_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        pass_frame.pack(pady=5)

        ctk.CTkLabel(pass_frame, text="🔒", font=("Segoe UI", 20), text_color=COLORS['accent_secondary'], width=40).pack(side="left")

        self.password_entry = ctk.CTkEntry(
            pass_frame, placeholder_text="Contraseña", width=300, height=45,
            font=("Segoe UI", 14), show="•", fg_color=COLORS['input_bg'],
            border_color=COLORS['accent_secondary'], border_width=2, corner_radius=10
        )
        self.password_entry.pack(side="left")

        # Recordar
        options_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=(15, 20))

        self.remember_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame, text="Recordar mi sesión", variable=self.remember_var,
            font=("Segoe UI", 12), fg_color=COLORS['accent_tertiary'],
            hover_color=COLORS['accent_secondary'], text_color=COLORS['text_secondary']
        ).pack(side="left")

        # Botones
        HoverButton(
            input_frame, text="INICIAR SESIÓN", width=340, height=50,
            font=("Segoe UI", 16, "bold"), fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'], corner_radius=10,
            command=self.iniciar_sesion
        ).pack(pady=(0, 10))

        ctk.CTkButton(
            input_frame, text="CREAR CUENTA NUEVA", width=340, height=45,
            font=("Segoe UI", 14), fg_color="transparent", hover_color=COLORS['bg_light'],
            text_color=COLORS['text_secondary'], border_width=2, border_color=COLORS['accent_tertiary'],
            corner_radius=10, command=self.mostrar_registro
        ).pack(pady=(0, 15))

        # Recuperar
        forgot_link = ctk.CTkLabel(
            input_frame, text="¿Olvidaste tu contraseña?", font=("Segoe UI", 12),
            text_color=COLORS['accent_secondary'], cursor="hand2"
        )
        forgot_link.pack(pady=5)
        forgot_link.bind("<Button-1>", self.recuperar_contraseña)

        # Footer
        ctk.CTkLabel(
            self.login_frame,
            text=f"© 2026 VibeFlow v{self.version_actual}. Todos los derechos reservados.",
            font=("Segoe UI", 10), text_color=COLORS['text_dim']
        ).pack(side="bottom", pady=20)

        if self.usuario_actual:
            self.username_entry.insert(0, self.usuario_actual)
            self.password_entry.focus()

    def recuperar_contraseña(self, event=None):
        recover_window = ctk.CTkToplevel(self)
        recover_window.title("Recuperar Contraseña")
        recover_window.geometry("400x300")
        recover_window.configure(fg_color=COLORS['bg_medium'])
        recover_window.transient(self)
        recover_window.grab_set()
        
        recover_window.update_idletasks()
        x = (self.winfo_width() - recover_window.winfo_width()) // 2 + self.winfo_x()
        y = (self.winfo_height() - recover_window.winfo_height()) // 2 + self.winfo_y()
        recover_window.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(
            recover_window, text="🔐 Recuperar Contraseña", font=("Segoe UI", 20, "bold"),
            text_color=COLORS['accent_primary']
        ).pack(pady=20)
        
        ctk.CTkLabel(
            recover_window, text="Ingresa tu correo electrónico\ny te enviaremos instrucciones",
            font=("Segoe UI", 12), text_color=COLORS['text_secondary'], justify="center"
        ).pack(pady=10)
        
        email_entry = ctk.CTkEntry(
            recover_window, placeholder_text="tu@email.com", width=250, height=40,
            font=("Segoe UI", 13), fg_color=COLORS['input_bg'],
            border_color=COLORS['accent_primary'], border_width=2, corner_radius=8
        )
        email_entry.pack(pady=20)
        
        def enviar_recuperacion():
            email = email_entry.get()
            if email:
                messagebox.showinfo("Correo Enviado", f"Se han enviado instrucciones a:\n{email}")
                recover_window.destroy()
        
        HoverButton(
            recover_window, text="ENVIAR INSTRUCCIONES", width=250, height=40,
            font=("Segoe UI", 13, "bold"), fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'], corner_radius=8, command=enviar_recuperacion
        ).pack(pady=10)
        
        ctk.CTkButton(
            recover_window, text="Cancelar", width=250, height=35,
            font=("Segoe UI", 12), fg_color="transparent", hover_color=COLORS['bg_light'],
            text_color=COLORS['text_secondary'], command=recover_window.destroy
        ).pack(pady=5)

    def mostrar_registro(self):
        self.login_frame.destroy()
        
        self.register_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'], corner_radius=30)
        self.register_frame.pack(expand=True, fill="both", padx=30, pady=30)

        center_frame = ctk.CTkFrame(self.register_frame, fg_color="transparent")
        center_frame.pack(expand=True)

        # Logo
        logo_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        logo_frame.pack(pady=(0, 10))

        colors = [COLORS['accent_primary'], COLORS['accent_secondary'], COLORS['accent_tertiary']]
        for color in colors:
            dot = ctk.CTkLabel(logo_frame, text="●", font=("Segoe UI", 40), text_color=color)
            dot.pack(side="left", padx=2)

        ctk.CTkLabel(
            center_frame, text="Únete a VibeFlow", font=("Segoe UI", 40, "bold"),
            text_color=COLORS['accent_primary']
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            center_frame, text="Crea tu cuenta y disfruta de la música",
            font=("Segoe UI", 14), text_color=COLORS['text_secondary']
        ).pack(pady=(0, 30))

        input_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        input_frame.pack(pady=10)

        # Campos
        fields = [
            ("👤", "Nombre de usuario", "reg_user", COLORS['accent_primary']),
            ("📧", "Correo electrónico", "reg_email", COLORS['accent_secondary']),
            ("🔒", "Contraseña", "reg_pass", COLORS['accent_tertiary'], True),
            ("🔒", "Confirmar contraseña", "reg_confirm", COLORS['accent_primary'], True)
        ]

        for field in fields:
            icon, placeholder, attr, color, *show = field
            is_password = show[0] if show else False
            
            field_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
            field_frame.pack(pady=5)

            ctk.CTkLabel(field_frame, text=icon, font=("Segoe UI", 20), text_color=color, width=40).pack(side="left")

            entry = ctk.CTkEntry(
                field_frame, placeholder_text=placeholder, width=300, height=45,
                font=("Segoe UI", 14), show="•" if is_password else "",
                fg_color=COLORS['input_bg'], border_color=color, border_width=2, corner_radius=10
            )
            entry.pack(side="left")
            setattr(self, attr, entry)

        # Términos
        terms_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        terms_frame.pack(fill="x", pady=(15, 20))

        self.terms_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            terms_frame, text="Acepto los Términos y Condiciones", variable=self.terms_var,
            font=("Segoe UI", 12), fg_color=COLORS['accent_tertiary'],
            hover_color=COLORS['accent_secondary'], text_color=COLORS['text_secondary']
        ).pack(side="left")

        # Botones
        HoverButton(
            input_frame, text="CREAR CUENTA", width=340, height=50,
            font=("Segoe UI", 16, "bold"), fg_color=COLORS['accent_secondary'],
            hover_color=COLORS['accent_hover'], corner_radius=10,
            command=self.registrar_usuario
        ).pack(pady=(0, 10))

        ctk.CTkButton(
            input_frame, text="← VOLVER AL LOGIN", width=340, height=45,
            font=("Segoe UI", 14), fg_color="transparent", hover_color=COLORS['bg_light'],
            text_color=COLORS['text_secondary'], border_width=2, border_color=COLORS['accent_primary'],
            corner_radius=10, command=self.volver_login
        ).pack()

        ctk.CTkLabel(
            self.register_frame, text=f"© 2026 VibeFlow v{self.version_actual}",
            font=("Segoe UI", 10), text_color=COLORS['text_dim']
        ).pack(side="bottom", pady=20)

    def volver_login(self):
        self.register_frame.destroy()
        self.crear_login()

    def iniciar_sesion(self):
        usuario = self.username_entry.get()
        password = self.password_entry.get()
        
        if usuario and password:
            self.usuario_actual = usuario
            self.guardar_configuracion()
            self.login_frame.destroy()
            self.construir_interfaz_principal()
        else:
            messagebox.showerror("Error", "Usuario y contraseña son requeridos")

    def registrar_usuario(self):
        usuario = self.reg_user.get()
        password = self.reg_pass.get()
        confirm = self.reg_confirm.get()
        
        if not usuario or not password:
            messagebox.showerror("Error", "Todos los campos son requeridos")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
            
        messagebox.showinfo("Éxito", "¡Cuenta creada correctamente! 🎉")
        self.volver_login()

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres cerrar sesión?"):
            pygame.mixer.music.stop()
            self.usuario_actual = None
            self.ruta_carpeta = ""
            self.canciones = []
            self.cancion_actual_idx = -1
            self.esta_reproduciendo = False
            for widget in self.winfo_children():
                widget.destroy()
            self.crear_login()

    def buscar_actualizaciones(self):
        self.actualizador.verificar(silencioso=False)

    def construir_interfaz_principal(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        self.sidebar = AnimatedSidebar(
            main_container, width_expanded=200, width_collapsed=50,
            on_logout=self.cerrar_sesion, on_check_updates=self.buscar_actualizaciones,
            fg_color=COLORS['bg_medium'], corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")

        # Botones de navegación
        self.btn_reproductor = self.sidebar.add_nav_button(
            "Reproducir", "🎵", lambda: self.cambiar_vista("reproductor")
        )
        
        self.btn_descargas = self.sidebar.add_nav_button(
            "Descargas", "📥", self.abrir_descargas
        )
        
        self.btn_biblioteca = self.sidebar.add_nav_button(
            "Biblioteca", "📚", self.abrir_biblioteca
        )
        
        self.btn_listas = self.sidebar.add_nav_button(
            "Listas", "📋", lambda: self.cambiar_vista("listas")
        )

        self.sidebar.set_user_info(self.usuario_actual)

        self.content_area = ctk.CTkFrame(main_container, fg_color=COLORS['bg_dark'], corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)

        self.view_reproductor = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.view_descargador = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.view_listas = ctk.CTkFrame(self.content_area, fg_color="transparent")

        self.setup_reproductor()
        self.setup_descargador()
        self.setup_listas()

        self.cambiar_vista("reproductor")
        self.btn_reproductor.configure(fg_color=COLORS['bg_light'], text_color=COLORS['text_primary'])
        
        self.after(3000, lambda: self.actualizador.verificar(silencioso=True))

    def abrir_descargas(self):
        if not self.ruta_carpeta:
            messagebox.showinfo("Info", "Selecciona una carpeta primero.")
            return
        VentanaDescargasProfesional(self, self.ruta_carpeta)

    def abrir_biblioteca(self):
        if not self.canciones:
            messagebox.showinfo("Info", "No hay canciones cargadas.\nSelecciona una carpeta primero.")
            return
        VentanaBiblioteca(
            self, self.canciones, self.ruta_carpeta,
            self.reproducir_idx, self.cargar_canciones
        )

    def cambiar_vista(self, vista):
        self.current_view = vista
        
        self.btn_reproductor.configure(fg_color="transparent", text_color=COLORS['text_secondary'])
        self.btn_descargas.configure(fg_color="transparent", text_color=COLORS['text_secondary'])
        self.btn_biblioteca.configure(fg_color="transparent", text_color=COLORS['text_secondary'])
        self.btn_listas.configure(fg_color="transparent", text_color=COLORS['text_secondary'])
        
        self.view_reproductor.pack_forget()
        self.view_descargador.pack_forget()
        self.view_listas.pack_forget()
        
        if vista == "reproductor":
            self.view_reproductor.pack(fill="both", expand=True)
            self.btn_reproductor.configure(fg_color=COLORS['bg_light'], text_color=COLORS['text_primary'])
        elif vista == "descargador":
            self.view_descargador.pack(fill="both", expand=True)
            self.btn_descargas.configure(fg_color=COLORS['bg_light'], text_color=COLORS['text_primary'])
        elif vista == "listas":
            self.view_listas.pack(fill="both", expand=True)
            self.btn_listas.configure(fg_color=COLORS['bg_light'], text_color=COLORS['text_primary'])

    def setup_reproductor(self):
        folder_frame = ctk.CTkFrame(self.view_reproductor, fg_color="transparent")
        folder_frame.pack(fill="x", padx=15, pady=10)

        self.folder_label = ctk.CTkLabel(
            folder_frame, text="📁 Sin carpeta", font=("Segoe UI", 14), text_color=COLORS['text_secondary']
        )
        self.folder_label.pack(side="left", padx=5)

        self.song_count_label = ctk.CTkLabel(
            folder_frame, text="(0)", font=("Segoe UI", 13), text_color=COLORS['text_dim']
        )
        self.song_count_label.pack(side="left", padx=3)

        folder_buttons = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_buttons.pack(side="right")

        HoverButton(
            folder_buttons, text="📂 Abrir", command=self.seleccionar_carpeta,
            fg_color=COLORS['accent_primary'], hover_color=COLORS['accent_hover'],
            width=80, height=35, font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=3)

        HoverButton(
            folder_buttons, text="🔄", command=self.cargar_canciones,
            fg_color=COLORS['bg_light'], hover_color=COLORS['accent_primary'],
            width=45, height=35, font=("Segoe UI", 16)
        ).pack(side="left", padx=3)

        main_frame = ctk.CTkFrame(self.view_reproductor, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(
            main_frame, text="📋 Lista de reproducción",
            font=("Segoe UI", 16, "bold"), text_color=COLORS['text_primary']
        ).pack(anchor="w", padx=15, pady=(5, 5))

        self.playlist_list = PlaylistList(
            main_frame,
            on_song_select=self.reproducir_idx,
            on_song_delete=self.eliminar_cancion
        )
        self.playlist_list.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        self.crear_controles()

        if self.ruta_carpeta and os.path.exists(self.ruta_carpeta):
            self.cargar_canciones()

    def eliminar_cancion(self, idx):
        if 0 <= idx < len(self.canciones):
            ruta = os.path.join(self.ruta_carpeta, self.canciones[idx])
            try:
                os.remove(ruta)
                self.cargar_canciones()
            except:
                pass

    def crear_controles(self):
        controls_frame = ctk.CTkFrame(
            self.view_reproductor, fg_color=COLORS['bg_medium'], corner_radius=10, height=180
        )
        controls_frame.pack(fill="x", padx=15, pady=(5, 15))
        controls_frame.pack_propagate(False)

        self.song_info = ctk.CTkLabel(
            controls_frame, text="No hay canción seleccionada",
            font=("Segoe UI", 15, "bold"), text_color=COLORS['text_primary']
        )
        self.song_info.pack(pady=(8, 5))

        self.progress_bar = ProgressBar(controls_frame, on_seek=self.cambiar_posicion)
        self.progress_bar.pack(fill="x", padx=20, pady=5)

        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.pack(pady=5)

        self.btn_shuffle = ctk.CTkButton(
            buttons_frame, text="🔀", width=40, height=40, fg_color=COLORS['bg_light'],
            hover_color=COLORS['accent_primary'], text_color=COLORS['text_primary'],
            font=("Segoe UI", 18), corner_radius=20, command=self.toggle_shuffle
        )
        self.btn_shuffle.grid(row=0, column=0, padx=3)

        self.btn_prev = ctk.CTkButton(
            buttons_frame, text="⏮", width=40, height=40, fg_color=COLORS['bg_light'],
            hover_color=COLORS['accent_primary'], text_color=COLORS['text_primary'],
            font=("Segoe UI", 18), corner_radius=20, command=self.cancion_anterior
        )
        self.btn_prev.grid(row=0, column=1, padx=3)

        self.btn_play = ctk.CTkButton(
            buttons_frame, text="▶", width=50, height=50, fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'], text_color=COLORS['text_primary'],
            font=("Segoe UI", 24), corner_radius=25, command=self.play_pause
        )
        self.btn_play.grid(row=0, column=2, padx=3)

        self.btn_next = ctk.CTkButton(
            buttons_frame, text="⏭", width=40, height=40, fg_color=COLORS['bg_light'],
            hover_color=COLORS['accent_primary'], text_color=COLORS['text_primary'],
            font=("Segoe UI", 18), corner_radius=20, command=self.cancion_siguiente
        )
        self.btn_next.grid(row=0, column=3, padx=3)

        self.btn_repeat = ctk.CTkButton(
            buttons_frame, text="🔁", width=40, height=40, fg_color=COLORS['bg_light'],
            hover_color=COLORS['accent_primary'], text_color=COLORS['text_primary'],
            font=("Segoe UI", 18), corner_radius=20, command=self.toggle_repeat
        )
        self.btn_repeat.grid(row=0, column=4, padx=3)

        volume_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        volume_frame.pack(fill="x", padx=20, pady=(5, 8))

        self.volume_control = VolumeControl(
            volume_frame, initial_volume=self.volumen, on_change=self.cambiar_volumen
        )
        self.volume_control.pack(fill="x", expand=True)

    def setup_descargador(self):
        frame = ctk.CTkFrame(self.view_descargador, fg_color=COLORS['bg_medium'], corner_radius=10)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(
            frame, text="📥 Descargar desde YouTube", font=("Segoe UI", 20, "bold"),
            text_color=COLORS['accent_primary']
        ).pack(pady=(25, 20))

        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(input_frame, text="URL del video:", font=("Segoe UI", 13),
                    text_color=COLORS['text_secondary']).pack(anchor="w")

        url_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        url_frame.pack(fill="x", pady=(3, 10))

        self.entry_url = ctk.CTkEntry(
            url_frame, placeholder_text="https://youtube.com/watch?v=...",
            height=38, font=("Segoe UI", 13), fg_color=COLORS['bg_light'],
            border_color=COLORS['accent_primary']
        )
        self.entry_url.pack(side="left", fill="x", expand=True)

        HoverButton(
            url_frame, text="📋", width=38, height=38, fg_color=COLORS['bg_light'],
            hover_color=COLORS['accent_primary'], font=("Segoe UI", 18),
            command=self.pegar_url
        ).pack(side="right", padx=(3, 0))

        options_frame = ctk.CTkFrame(frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=30, pady=5)

        self.quality_var = ctk.StringVar(value="192 kbps")
        ctk.CTkOptionMenu(
            options_frame, values=["128 kbps", "192 kbps", "320 kbps"],
            variable=self.quality_var, fg_color=COLORS['bg_light'],
            button_color=COLORS['accent_primary'], button_hover_color=COLORS['accent_hover'],
            text_color=COLORS['text_primary'], width=110, height=32
        ).pack(side="left", padx=3)

        self.format_var = ctk.StringVar(value="mp3")
        ctk.CTkOptionMenu(
            options_frame, values=["mp3", "m4a", "wav"], variable=self.format_var,
            fg_color=COLORS['bg_light'], button_color=COLORS['accent_primary'],
            button_hover_color=COLORS['accent_hover'], text_color=COLORS['text_primary'],
            width=90, height=32
        ).pack(side="left", padx=3)

        self.btn_descargar = HoverButton(
            frame, text="⬇ DESCARGAR", height=42, fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'], font=("Segoe UI", 14, "bold"),
            command=self.iniciar_descarga
        )
        self.btn_descargar.pack(pady=15, padx=30, fill="x")

        status_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_light'], corner_radius=8)
        status_frame.pack(fill="x", padx=30, pady=10)

        self.label_status = ctk.CTkLabel(
            status_frame, text="✅ Listo para descargar", font=("Segoe UI", 13),
            text_color=COLORS['text_secondary']
        )
        self.label_status.pack(pady=10)

        self.progress_descarga = ctk.CTkProgressBar(
            status_frame, height=8, fg_color=COLORS['bg_medium'],
            progress_color=COLORS['accent_primary']
        )
        self.progress_descarga.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_descarga.set(0)

    def setup_listas(self):
        frame = ctk.CTkFrame(self.view_listas, fg_color=COLORS['bg_medium'], corner_radius=10)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(
            frame, text="📋 Mis Listas de Reproducción", font=("Segoe UI", 20, "bold"),
            text_color=COLORS['accent_primary']
        ).pack(pady=(25, 15))

        coming_soon_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_light'], corner_radius=8)
        coming_soon_frame.pack(expand=True, fill="both", padx=30, pady=15)

        ctk.CTkLabel(
            coming_soon_frame,
            text="✨ PRÓXIMAMENTE ✨\n\n🎯 Gestión de listas de reproducción",
            font=("Segoe UI", 15), text_color=COLORS['text_secondary'], justify="center"
        ).pack(expand=True)

    def pegar_url(self):
        try:
            url = self.clipboard_get()
            self.entry_url.delete(0, 'end')
            self.entry_url.insert(0, url)
        except:
            pass

    def progreso_hook(self, d):
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', 1)
                progress = downloaded / total
                
                def update_progress():
                    self.progress_descarga.set(progress)
                    percent = int(progress * 100)
                    speed = d.get('speed', 0)
                    if speed:
                        speed_mb = speed / 1024 / 1024
                        self.label_status.configure(
                            text=f"⬇ Descargando... {percent}% ({speed_mb:.1f} MB/s)"
                        )
                    else:
                        self.label_status.configure(text=f"⬇ Descargando... {percent}%")
                
                self.after(0, update_progress)
                
        elif d['status'] == 'finished':
            def finished():
                self.label_status.configure(text="🔄 Procesando audio...")
                self.progress_descarga.set(1.0)
            self.after(0, finished)

    def iniciar_descarga(self):
        url = self.entry_url.get().strip()
        
        if not url:
            messagebox.showwarning("Aviso", "Por favor, pega un enlace de YouTube")
            return
            
        if not self.ruta_carpeta or not os.path.exists(self.ruta_carpeta):
            messagebox.showwarning("Aviso", "Primero selecciona una carpeta")
            return
            
        if self.descarga_en_progreso:
            messagebox.showinfo("Info", "Ya hay una descarga en curso")
            return

        quality = self.quality_var.get().split()[0]
        format_type = self.format_var.get()

        self.descarga_en_progreso = True
        self.btn_descargar.configure(state="disabled", text="⬇ Descargando...")
        self.progress_descarga.set(0)
        self.label_status.configure(text="🔄 Iniciando descarga...")

        thread = threading.Thread(
            target=self._descargar, args=(url, quality, format_type), daemon=True
        )
        thread.start()

    def _descargar(self, url, quality, format_type):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.ruta_carpeta, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format_type,
                'preferredquality': quality,
            }],
            'progress_hooks': [self.progreso_hook],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            def success():
                self.label_status.configure(text="✅ ¡Descarga completada!")
                self.progress_descarga.set(1.0)
                self.btn_descargar.configure(state="normal", text="⬇ DESCARGAR")
                self.descarga_en_progreso = False
                self.entry_url.delete(0, 'end')
                self.cargar_canciones()
                messagebox.showinfo("Éxito", "Canción descargada correctamente")
            
            self.after(0, success)

        except Exception as e:
            def error():
                self.label_status.configure(text="❌ Error en la descarga")
                self.btn_descargar.configure(state="normal", text="⬇ DESCARGAR")
                self.descarga_en_progreso = False
                self.progress_descarga.set(0)
                messagebox.showerror("Error", f"Error en la descarga:\n{str(e)}")
            
            self.after(0, error)

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Selecciona tu carpeta de música")
        if carpeta:
            self.ruta_carpeta = carpeta
            self.folder_label.configure(text=f"📁 {os.path.basename(carpeta)}")
            self.guardar_configuracion()
            self.cargar_canciones()

    def cargar_canciones(self):
        if not self.ruta_carpeta or not os.path.exists(self.ruta_carpeta):
            return

        self.canciones = []
        formatos = ('.mp3', '.wav', '.flac', '.m4a', '.ogg')
        
        try:
            for archivo in os.listdir(self.ruta_carpeta):
                if archivo.lower().endswith(formatos):
                    self.canciones.append(archivo)
            
            self.canciones.sort(key=str.lower)
            self.playlist_list.update_songs(self.canciones, self.cancion_actual_idx)
            self.song_count_label.configure(text=f"({len(self.canciones)})")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las canciones:\n{str(e)}")

    def reproducir_idx(self, idx):
        if 0 <= idx < len(self.canciones):
            self.cancion_actual_idx = idx
            ruta_completa = os.path.join(self.ruta_carpeta, self.canciones[idx])
            
            try:
                pygame.mixer.music.stop()
                time.sleep(0.1)
                
                pygame.mixer.music.load(ruta_completa)
                pygame.mixer.music.play()
                self.esta_reproduciendo = True
                self.pausado = False
                self.posicion_actual = 0
                self.btn_play.configure(text="⏸")
                
                try:
                    audio = MutagenFile(ruta_completa)
                    self.duracion_actual = audio.info.length if audio else 0
                except:
                    self.duracion_actual = 0
                
                nombre_limpio = os.path.splitext(self.canciones[idx])[0]
                if len(nombre_limpio) > 40:
                    nombre_limpio = nombre_limpio[:37] + "..."
                self.song_info.configure(text=nombre_limpio)
                
                self.playlist_list.highlight_current(idx)
                
                self.progress_bar.reset()
                self.progress_bar.total_time = self.duracion_actual
                
                self.actualizar_progreso()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reproducir:\n{str(e)}")

    def play_pause(self):
        if self.cancion_actual_idx >= 0:
            if self.esta_reproduciendo and not self.pausado:
                pygame.mixer.music.pause()
                self.pausado = True
                self.btn_play.configure(text="▶")
            elif self.pausado:
                pygame.mixer.music.unpause()
                self.pausado = False
                self.btn_play.configure(text="⏸")
                self.actualizar_progreso()
            else:
                ruta_completa = os.path.join(self.ruta_carpeta, self.canciones[self.cancion_actual_idx])
                try:
                    pygame.mixer.music.load(ruta_completa)
                    pygame.mixer.music.play()
                    self.esta_reproduciendo = True
                    self.pausado = False
                    self.btn_play.configure(text="⏸")
                    self.actualizar_progreso()
                except:
                    pass

    def cancion_siguiente(self):
        if self.canciones:
            if self.shuffle:
                idx = random.randint(0, len(self.canciones)-1)
            else:
                idx = (self.cancion_actual_idx + 1) % len(self.canciones)
            self.reproducir_idx(idx)

    def cancion_anterior(self):
        if self.canciones:
            if self.shuffle:
                idx = random.randint(0, len(self.canciones)-1)
            else:
                idx = (self.cancion_actual_idx - 1) % len(self.canciones)
            self.reproducir_idx(idx)

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self.btn_shuffle.configure(
            fg_color=COLORS['accent_primary'] if self.shuffle else COLORS['bg_light']
        )

    def toggle_repeat(self):
        self.repeat = not self.repeat
        self.btn_repeat.configure(
            fg_color=COLORS['accent_primary'] if self.repeat else COLORS['bg_light']
        )

    def cambiar_volumen(self, valor):
        self.volumen = float(valor)
        pygame.mixer.music.set_volume(self.volumen)
        self.guardar_configuracion()

    def cambiar_posicion(self, valor):
        if self.cancion_actual_idx >= 0 and self.duracion_actual > 0:
            nueva_pos = (float(valor) / 100) * self.duracion_actual
            if self.pausado:
                self.posicion_actual = nueva_pos
            else:
                pygame.mixer.music.play(start=nueva_pos)
                self.posicion_actual = nueva_pos

    def actualizar_progreso(self):
        if self.cancion_actual_idx >= 0 and self.esta_reproduciendo and not self.pausado:
            try:
                if pygame.mixer.music.get_busy():
                    pos = pygame.mixer.music.get_pos() / 1000 + self.posicion_actual
                    if pos > self.duracion_actual and self.duracion_actual > 0:
                        pos = self.duracion_actual
                    self.progress_bar.set_progress(pos, self.duracion_actual)
                    self.after(500, self.actualizar_progreso)
                else:
                    if self.repeat:
                        self.posicion_actual = 0
                        self.reproducir_idx(self.cancion_actual_idx)
                    else:
                        self.cancion_siguiente()
            except:
                self.after(500, self.actualizar_progreso)

# ============================================
# INICIO DE LA APLICACIÓN
# ============================================

if __name__ == "__main__":
    app = VibeFlow()
    app.mainloop()