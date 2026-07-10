"""
Módulo: config_api.py

Descripción:
Gestiona la configuración de acceso a la API de YouTube Data v3 utilizada por
el agente inteligente adaptativo. Este módulo permite solicitar, validar,
almacenar y recuperar la API Key necesaria para establecer la comunicación con
el servicio de YouTube.

Responsabilidades:
- Solicitar al usuario una API Key de YouTube Data v3.
- Validar la API Key mediante una consulta de prueba a la API.
- Almacenar la configuración localmente para reutilizarla en futuras ejecuciones.
- Recuperar la configuración almacenada durante el inicio del sistema.
- Inicializar la configuración necesaria para el funcionamiento del agente.

Integración dentro del agente:
Este módulo se ejecuta durante la inicialización del sistema para verificar que
exista una API Key válida antes de habilitar la recuperación de recursos
educativos desde YouTube.

Dependencias:
- json
- tkinter
- requests
- webbrowser
- modulos.rutas

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de videos
educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""
import json
import tkinter as tk
import webbrowser

import requests

from tkinter import messagebox

from modulos.rutas import API_FILE


def validar_api_key(api_key):
    """
    Valida la API Key mediante una consulta de prueba a la API de YouTube Data v3.

    Parámetros:
        api_key (str): Clave de acceso proporcionada por el usuario.

    Retorna:
        bool:
            True si la API Key permite acceder correctamente a la API de
            YouTube Data v3; False en cualquier otro caso.

    Esta validación verifica que la clave pueda establecer comunicación con
    la API y recuperar al menos un recurso educativo antes de almacenarla
    para futuras ejecuciones del sistema.
    """

    youtube_search_url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": "educación",
        "type": "video",
        "maxResults": 1,
        "key": api_key
    }

    try:
        response = requests.get(
            youtube_search_url,
            params=params,
            timeout=5
        )

        respuesta_json = response.json()

        if (
            response.status_code == 200
            and "items" in respuesta_json
            and len(respuesta_json["items"]) > 0
        ):
            return True

        if "error" in respuesta_json:
            return False

        return False

    except requests.exceptions.Timeout:
        return False

    except requests.exceptions.ConnectionError:
        return False

    except requests.exceptions.RequestException:
        return False


def guardar_api_key(api_key, ventana):
    """
    Valida y almacena la API Key proporcionada por el usuario.

    Parámetros:
        api_key (str): API Key de YouTube Data v3 ingresada por el usuario.
        ventana (tk.Toplevel): Ventana de configuración de la API.

    La función verifica que la API Key no esté vacía, valida su acceso a la
    API de YouTube Data v3 y, si es correcta, la almacena localmente para
    futuras ejecuciones del sistema.
    """

    if not api_key.strip():
        messagebox.showwarning(
            "Campo obligatorio",
            "Ingrese una API Key de YouTube para continuar."
        )
        return

    if not validar_api_key(api_key):
        messagebox.showerror(
            "No fue posible validar la API Key",
            "Verifique que:\n\n"
            "• La API Key sea correcta.\n"
            "• La API de YouTube Data v3 esté habilitada.\n"
            "• Exista conexión a Internet.\n\n"
            "Después, intente nuevamente."
        )
        return

    with open(API_FILE, "w", encoding="utf-8") as archivo:
        json.dump(
            {"api_key": api_key},
            archivo,
            indent=4,
            ensure_ascii=False
        )

    messagebox.showinfo(
        "Configuración completada",
        "La API Key fue validada correctamente y se guardó para futuras "
        "ejecuciones del sistema."
    )

    ventana.destroy()


def cargar_api_key():
    """
    Recupera la API Key almacenada localmente.

    Retorna:
        str | None:
            Devuelve la API Key almacenada si existe y puede leerse
            correctamente. En caso contrario, devuelve None.
    """

    if not API_FILE.exists():
        return None

    try:
        with open(API_FILE, "r", encoding="utf-8") as archivo:
            configuracion = json.load(archivo)
            return configuracion.get("api_key")

    except (OSError, json.JSONDecodeError):
        return None


def mostrar_info_api():
    """
    Muestra información sobre la API de YouTube Data v3 y ofrece al usuario
    la posibilidad de abrir la página oficial de Google Cloud para obtener
    una API Key.
    """

    mensaje = (
        "Para utilizar el agente inteligente es necesario disponer de una "
        "API Key de YouTube Data v3.\n\n"
        "Esta credencial permite establecer comunicación con la API oficial "
        "de YouTube para recuperar información de los videos educativos "
        "utilizados por el sistema.\n\n"
        "¿Desea abrir la página oficial de Google Cloud para obtener una "
        "API Key?"
    )

    if messagebox.askyesno(
        "Configuración de la API de YouTube",
        mensaje
    ):
        webbrowser.open(
            "https://console.cloud.google.com/apis/credentials"
        )


def ventana_api_key(root):
    """
    Crea la ventana para configurar la API Key de YouTube Data v3.

    Parámetros:
        root (tk.Tk): Ventana principal de la aplicación.

    Retorna:
        tk.Toplevel:
            Ventana de configuración utilizada durante la inicialización
            del agente inteligente.
    """

    ventana = tk.Toplevel(root)
    ventana.title("Configuración de la API de YouTube")
    ventana.geometry("450x250")
    ventana.resizable(False, False)

    tk.Label(
        ventana,
        text=(
            "Ingrese la API Key de YouTube Data v3.\n\n"
            "La clave será validada antes de almacenarse en la "
            "configuración del sistema."
        ),
        wraplength=350,
        justify="center"
    ).pack(pady=15)

    entry = tk.Entry(ventana, width=50)
    entry.pack(pady=10)

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=20)

    tk.Button(
        frame_botones,
        text="Validar y guardar",
        width=15,
        command=lambda: guardar_api_key(entry.get(), ventana)
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        frame_botones,
        text="¿Cómo obtener una API Key?",
        width=22,
        command=mostrar_info_api
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        frame_botones,
        text="Cancelar",
        width=10,
        command=ventana.destroy
    ).grid(row=0, column=2, padx=5)

    return ventana


def inicializar_api(root):
    """
    Inicializa la configuración de acceso a la API de YouTube Data v3.

    Parámetros:
        root (tk.Tk): Ventana principal de la aplicación.

    Retorna:
        str | None:
            Devuelve la API Key validada cuando la configuración es correcta.
            Si no es posible obtener una API Key válida, devuelve None.

    Esta función garantiza que el agente inteligente disponga de una API Key
    funcional antes de iniciar la recuperación de recursos educativos desde
    YouTube.
    """

    api_key = cargar_api_key()

    if not api_key:
        ventana = ventana_api_key(root)
        root.wait_window(ventana)

        api_key = cargar_api_key()

    if not api_key:
        return None

    if not validar_api_key(api_key):
        ventana = ventana_api_key(root)
        root.wait_window(ventana)

        api_key = cargar_api_key()

        if not api_key:
            return None

    return api_key

