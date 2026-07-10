"""
Módulo: main.py

Descripción:
Punto de entrada del artefacto. Coordina la inicialización de los
componentes principales del sistema, incluyendo la configuración de la
API de YouTube, el perfil docente y la interfaz gráfica del agente.

Responsabilidades:
- Inicializar el entorno de ejecución.
- Configurar la API de YouTube.
- Inicializar el perfil docente.
- Iniciar la interfaz principal del agente.

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de
videos educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""
import tkinter as tk

from modulos.config_api import inicializar_api
from modulos.perfil_docente import inicializar_perfil
from modulos.main_ui import ventana_principal




def main():
    """
    Inicializa el artefacto y coordina la secuencia principal de
    ejecución.

    El proceso comprende la configuración de la API de YouTube, la
    inicialización del perfil docente y el despliegue de la interfaz
    principal del agente inteligente adaptativo.
    """

    root = tk.Tk()
    root.withdraw()

    # Configura la API de YouTube.

    api_key = inicializar_api(root)

    if not api_key:
        return

    # Inicializa el perfil docente.

    perfil = inicializar_perfil(root)

    if not perfil:
        return

    # Inicia la interfaz principal del agente.

    ventana_principal(
        root,
        api_key,
        perfil
    )

    root.mainloop()

# Ejecución

if __name__ == "__main__":
    main()
