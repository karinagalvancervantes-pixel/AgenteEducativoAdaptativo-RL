"""
Módulo: rutas.py

Descripción:
Centraliza la gestión de rutas utilizadas por el agente inteligente
adaptativo para almacenar la configuración y los datos persistentes.

El módulo garantiza que la estructura de almacenamiento sea compatible
con Windows, macOS y distribuciones Linux, creando automáticamente los
directorios necesarios durante la primera ejecución.

Autora:
Karina Galván Cervantes
"""

from pathlib import Path

# Directorio personal del usuario
HOME_DIR = Path.home()

# Directorio principal donde el agente almacena sus datos
APP_DIR = HOME_DIR / "AgenteEducativo-RL"

# Directorios internos
CONFIG_DIR = APP_DIR / "config"
DATA_DIR = APP_DIR / "data"

# Crear directorios automáticamente
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Archivos de configuración
API_FILE = CONFIG_DIR / "config_api.json"
PERFIL_FILE = CONFIG_DIR / "perfil_docente.json"

# Archivos de aprendizaje
HISTORIAL_FILE = DATA_DIR / "historial_evaluaciones.json"
Q_TABLE_FILE = DATA_DIR / "q_table.json"
