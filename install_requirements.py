"""
Script de instalación de dependencias
Ejecutar antes de usar la aplicación por primera vez
"""

import subprocess
import sys
import os

def install_requirements():
    """Instala todas las dependencias necesarias"""
    
    requirements = [
        "customtkinter>=5.0.0",
        "yt-dlp>=2023.0.0",
        "pygame>=2.1.0",
        "mutagen>=1.45.0",
        "pywinstyles>=1.0.0",  # Solo Windows
    ]
    
    print("📦 Instalando dependencias de VibeFlow...")
    print("=" * 50)
    
    for package in requirements:
        print(f"\n⏳ Instalando {package}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                package, "--upgrade"
            ])
            print(f"✅ {package} instalado correctamente")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  No se pudo instalar {package}: {e}")
            continue
    
    print("\n" + "=" * 50)
    print("✅ Instalación completada")
    print("\n📋 Próximos pasos:")
    print("1. Coloca FFmpeg en la carpeta de la aplicación")
    print("2. Ejecuta: python build_exe.py")
    print("3. Tu .exe estará en la carpeta 'dist'")

if __name__ == "__main__":
    install_requirements()
