"""
Script para automatizar el proceso de release mensual
Uso: python release.py
"""

import os
import json
import subprocess
import sys
from datetime import datetime

def get_version_info():
    """Obtiene info de version.json"""
    with open("version.json", "r") as f:
        return json.load(f)

def update_version(new_version):
    """Actualiza version.json"""
    with open("version.json", "r") as f:
        data = json.load(f)
    
    data["version"] = new_version
    data["release_date"] = datetime.now().strftime("%Y-%m-%d")
    
    with open("version.json", "w") as f:
        json.dump(data, f, indent=2)

def run_command(cmd, description):
    """Ejecuta comando y maneja errores"""
    print(f"\n⏳ {description}...")
    print(f"  Comando: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} completado")
        return True
    else:
        print(f"❌ Error: {result.stderr}")
        return False

def main():
    print("🚀 ASISTENTE DE RELEASE - VIBEFLOW")
    print("=" * 50)
    
    # Obtener versión actual
    current_version = get_version_info()["version"]
    print(f"\n📍 Versión actual: {current_version}")
    
    # Solicitar nueva versión
    print("\nEjemplos de versiones:")
    print("  1.0.4 → 1.0.5 (bug fix)")
    print("  1.0.5 → 1.1.0 (nueva característica)")
    print("  1.1.0 → 2.0.0 (cambio mayor)")
    
    new_version = input("\n¿Cuál es la nueva versión? ").strip()
    
    if not new_version:
        print("❌ Versión requerida")
        return
    
    # Solicitar descripción de cambios
    print("\n📝 Describe los cambios (presiona Enter dos veces para terminar):")
    lines = []
    while True:
        line = input()
        if line == "":
            if lines and lines[-1] == "":
                lines.pop()
                break
        lines.append(line)
    
    changelog = "\n".join(lines)
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RELEASE")
    print("=" * 50)
    print(f"Versión actual: {current_version}")
    print(f"Nueva versión:  {new_version}")
    print(f"Cambios:\n{changelog}")
    print("=" * 50)
    
    confirm = input("\n¿Proceder con el release? (s/n): ").strip().lower()
    if confirm != "s":
        print("❌ Release cancelado")
        return
    
    # PASO 1: Actualizar version.json
    print("\n🔧 PASO 1: Actualizar version.json")
    update_version(new_version)
    print("✅ version.json actualizado")
    
    # PASO 2: Compilar a .exe
    print("\n🔧 PASO 2: Compilar a ejecutable")
    if not run_command("python build_exe.py", "Compilación"):
        print("⚠️  La compilación falló. ¿Continuar igualmente? (s/n): ")
        if input().strip().lower() != "s":
            return
    
    # PASO 3: Git add y commit
    print("\n🔧 PASO 3: Preparar cambios para Git")
    if not run_command("git add .", "Git add"):
        return
    
    commit_msg = f'Version {new_version} - {changelog.split(chr(10))[0]}'
    if not run_command(f'git commit -m "{commit_msg}"', "Git commit"):
        return
    
    # PASO 4: Crear tag
    print("\n🔧 PASO 4: Crear tag de versión")
    if not run_command(f"git tag v{new_version}", "Crear tag"):
        return
    
    # PASO 5: Push a GitHub
    print("\n🔧 PASO 5: Subir a GitHub")
    if not run_command("git push origin main", "Push cambios"):
        return
    
    if not run_command("git push origin --tags", "Push tags"):
        return
    
    # Información final
    print("\n" + "=" * 50)
    print("✅ RELEASE COMPLETADO CON ÉXITO")
    print("=" * 50)
    print(f"\n📦 Versión: v{new_version}")
    print(f"📍 Branch: main")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🔗 Próximos pasos:")
    print(f"1. Ve a: https://github.com/tu-usuario/vibeflow-releases/releases/tag/v{new_version}")
    print("2. Haz clic en 'Create release from tag'")
    print("3. En descripción, pega el changelog:")
    print(f"\n{changelog}")
    print("\n4. Sube el archivo: dist/reproductor.exe")
    print("5. Publica el Release")
    
    print("\n💾 Backup:")
    backup_name = f"vibeflow_v{new_version}_BACKUP_{datetime.now().strftime('%Y%m%d')}"
    print(f"Considera hacer backup de tu carpeta con nombre: {backup_name}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Release cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
