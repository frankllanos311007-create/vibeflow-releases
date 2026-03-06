"""
Script para compilar VibeFlow a ejecutable (.exe)
Ejecutar: python build_exe.py
"""

import os
import shutil
import subprocess
import sys

def build_exe():
    """Compila la aplicación a ejecutable"""
    
    print("🔧 Iniciando compilación de VibeFlow...")
    
    # Verificar dependencias
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("⚠️  Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Rutas
    SCRIPT = "reproductor.py"
    ICON = "icono.ico"  # Asegúrate que exista
    OUTPUT_DIR = "dist"
    
    # Verificar archivo Python
    if not os.path.exists(SCRIPT):
        print(f"❌ Error: No se encontró {SCRIPT}")
        return False
    
    print(f"📝 Script encontrado: {SCRIPT}")
    
    # Limpiar builds anteriores
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    if os.path.exists("reproductor.spec"):
        os.remove("reproductor.spec")
    
    print("🧹 Carpetas anteriores limpiadas")
    
    # Comando PyInstaller
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",  # Un solo archivo ejecutable
        "--windowed",  # Sin ventana de consola
        "--add-data", "reproductor.py:.",
    ]
    
    # Añadir icono si existe
    if os.path.exists(ICON):
        cmd.extend(["--icon", ICON])
        print(f"🎨 Icono encontrado: {ICON}")
    
    cmd.append(SCRIPT)
    
    print("⚙️  Compilando... (esto puede tardar 1-2 minutos)")
    print(f"Comando: {' '.join(cmd)}")
    
    # Ejecutar PyInstaller
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Compilación exitosa!")
        
        exe_path = os.path.join(OUTPUT_DIR, "reproductor.exe")
        if os.path.exists(exe_path):
            print(f"\n🎉 Ejecutable creado: {exe_path}")
            print(f"📦 Tamaño: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
            return True
        else:
            print("❌ El ejecutable no fue creado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en la compilación: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
