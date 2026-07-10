"""
Módulo: perfil_docente.py

Descripción:
Gestiona el registro, almacenamiento y recuperación del perfil inicial del
docente utilizado por el agente inteligente adaptativo. La información
capturada permite contextualizar las búsquedas realizadas en YouTube y
constituye la base para el proceso posterior de personalización mediante
aprendizaje por refuerzo.

Responsabilidades:
- Registrar el perfil inicial del docente.
- Almacenar la información del perfil localmente.
- Recuperar la configuración almacenada en ejecuciones posteriores.
- Normalizar el área disciplinar y las palabras clave.
- Inicializar la configuración necesaria para el funcionamiento del agente.

Integración dentro del agente:
Este módulo se ejecuta durante la inicialización del sistema y proporciona
el perfil inicial que posteriormente utilizan los módulos de recuperación,
filtrado, aprendizaje adaptativo y recomendación.

Dependencias:
- json
- tkinter
- tkinter.ttk
- modulos.rutas

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de
videos educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""

import json
import tkinter as tk
from tkinter import messagebox, ttk

from modulos.rutas import PERFIL_FILE


def guardar_perfil(perfil, ventana):
    """
    Almacena el perfil del docente en el archivo de configuración local.

    Parámetros:
        perfil (dict): Información del perfil docente.
        ventana (tk.Toplevel): Ventana de configuración que será cerrada
            una vez almacenada la información.
    """

    with open(
        PERFIL_FILE,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            perfil,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    ventana.destroy()

    messagebox.showinfo(
        "Perfil guardado",
        "La información del perfil docente se almacenó correctamente."
    )


def cargar_perfil():
    """
    Recupera el perfil docente almacenado localmente.

    Retorna:
        dict | None:
            Devuelve el perfil almacenado cuando existe un archivo válido.
            En caso contrario devuelve None.
    """

    if not PERFIL_FILE.exists():
        return None

    try:

        with open(
            PERFIL_FILE,
            "r",
            encoding="utf-8"
        ) as archivo:

            perfil = json.load(archivo)

    except (OSError, json.JSONDecodeError):

        return None

    perfil.setdefault("perfil_adaptativo", {})

    adaptativo = perfil["perfil_adaptativo"]

    adaptativo.setdefault(
        "contador_tipo",
        {
            "teorico": 0,
            "practico": 0,
            "mixto": 0
        }
    )

    adaptativo.setdefault(
        "canales_preferidos",
        {}
    )

    adaptativo.setdefault(
        "tipo_preferido",
        None
    )

    return perfil


def mostrar_info_perfil():
    """
    Muestra información general sobre la finalidad del perfil docente.
    """

    messagebox.showinfo(
        "Información del perfil docente",
        "El perfil docente permite definir el contexto inicial del agente "
        "inteligente adaptativo.\n\n"
        "La información registrada se utiliza para personalizar las "
        "búsquedas de recursos educativos y posteriormente se complementa "
        "mediante el aprendizaje obtenido a partir de las evaluaciones "
        "realizadas por el docente."
    )


def normalizar_area(texto):
    """
    Normaliza el nombre del área disciplinar.

    Parámetros:
        texto (str): Área ingresada por el usuario.

    Retorna:
        str:
            Nombre del área con formato normalizado.
    """

    return texto.strip().lower().capitalize()


def limpiar_palabras_clave(texto):
    """
    Normaliza la lista de palabras clave ingresadas por el docente.

    Parámetros:
        texto (str): Cadena con palabras separadas por comas.

    Retorna:
        str:
            Cadena normalizada con las palabras clave.
    """

    palabras = [

        palabra.strip().lower()

        for palabra in texto.split(",")

        if palabra.strip()

    ]

    return ", ".join(palabras)


def ventana_perfil_docente(root):
    """
    Crea la ventana para registrar o actualizar el perfil inicial del docente.

    Parámetros:
        root (tk.Tk): Ventana principal de la aplicación.

    Retorna:
        tk.Toplevel:
            Ventana utilizada para capturar la información del perfil docente.
    """

    ventana = tk.Toplevel(root)
    ventana.title("Configuración del perfil docente")
    ventana.geometry("340x390")
    ventana.resizable(False, False)

    perfil_existente = cargar_perfil()

    if perfil_existente:
        perfil_inicial = perfil_existente.get("perfil_inicial", {})
    else:
        perfil_inicial = {}

    area_guardada = perfil_inicial.get("area", "")

    area_var = tk.StringVar(value=area_guardada)

    idioma_var = tk.StringVar(
        value=perfil_inicial.get("idioma", "").lower()
    )

    palabras_clave_var = tk.StringVar(
        value=perfil_inicial.get("palabras_clave", "")
    )

    areas_base = [
        "Programación",
        "Redes",
        "Matemáticas",
        "Ciencias",
        "Física"
    ]

    if area_guardada not in areas_base:
        area_otro_var = tk.StringVar(value=area_guardada)
    else:
        area_otro_var = tk.StringVar()

    tk.Label(
        ventana,
        text="Configuración del perfil docente",
        font=("Arial", 13, "bold")
    ).pack(pady=10)

    frame = tk.Frame(ventana)
    frame.pack(pady=5)

    frame_area = tk.Frame(frame)
    frame_area.pack(pady=5)

    tk.Label(
        frame_area,
        text="Área disciplinar"
    ).pack()

    if area_guardada and area_guardada not in areas_base:
        areas_base.append(area_guardada)

    if "Otro" not in areas_base:
        areas_base.append("Otro")

    area_cb = ttk.Combobox(
        frame_area,
        textvariable=area_var,
        values=areas_base,
        state="readonly"
    )
    area_cb.pack()

    label_especifique = tk.Label(
        frame_area,
        text="Especifique el área:"
    )

    area_otro_entry = tk.Entry(
        frame_area,
        textvariable=area_otro_var
    )

    def mostrar_sugerencia_idioma(event=None):
        """
        Muestra una recomendación cuando el docente selecciona
        la opción 'Ambos' como idioma de búsqueda.
        """

        if idioma_var.get() == "ambos":

            label_idioma_ambos.pack(
                pady=(5, 5),
                anchor="w"
            )

        else:

            label_idioma_ambos.pack_forget()

    
    def mostrar_otro(event=None):
        """
        Muestra u oculta el campo para capturar un área disciplinar
        personalizada.
        """

        if area_var.get() == "Otro":
            label_especifique.pack(pady=(5, 0))
            area_otro_entry.pack(pady=(0, 10))
        else:
            label_especifique.pack_forget()
            area_otro_entry.pack_forget()

    area_cb.bind(
        "<<ComboboxSelected>>",
        mostrar_otro
    )


    tk.Label(
        frame,
        text="Idioma"
    ).pack()

    idioma_cb = ttk.Combobox(
        frame,
        textvariable=idioma_var,
        values=[
            "español",
            "inglés",
            "ambos"
        ],
        state="readonly"
    )

    idioma_cb.pack()

    idioma_cb.bind(
        "<<ComboboxSelected>>",
        mostrar_sugerencia_idioma
    )
    

    label_idioma_ambos = tk.Label(
        frame,
        text=(
            "Sugerencia:\n"
            "Si selecciona \"Ambos\", registre palabras clave\n"
            "en español e inglés para obtener una mayor\n"
            "diversidad de recursos educativos.\n\n"
            "Ejemplo:\n"
            "redes, networking, switching"
        ),
        justify="left",
        fg="blue",
        font=("Arial", 8, "italic")
    )

    tk.Label(
        frame,
        text="Palabras clave del tema (separadas por comas)"
    ).pack(pady=(10, 0))

    tk.Entry(
        frame,
        textvariable=palabras_clave_var,
        width=40
    ).pack()

    frame_botones = tk.Frame(frame)
    frame_botones.pack(pady=15)

            
    def guardar():
        """
        Valida la información capturada y actualiza el perfil docente.
        """

        if not area_var.get().strip():
            messagebox.showwarning(
                "Área disciplinar",
                "Seleccione un área disciplinar."
            )
            return

        if perfil_existente:
            nuevo_perfil = perfil_existente
        else:
            nuevo_perfil = {
                "perfil_adaptativo": {}
            }

        if area_var.get() == "Otro":

            area_final = area_otro_var.get().strip()

            if not area_final:

                messagebox.showwarning(
                    "Área disciplinar",
                    "Especifique el área disciplinar."
                )
                return

            area_final = normalizar_area(area_final)

        else:

            area_final = normalizar_area(
                area_var.get()
            )

        palabras_limpias = limpiar_palabras_clave(
            palabras_clave_var.get()
        )

        if len(palabras_limpias.split(",")) > 5:

            messagebox.showwarning(
                "Palabras clave",
                "Puede registrar como máximo cinco palabras clave."
            )
            return

        nuevo_perfil["perfil_inicial"] = {
            "area": area_final,
            "idioma": idioma_var.get().strip().lower(),
            "duracion_preferida": "indefinido",
            "palabras_clave": palabras_limpias,
            "palabras_clave_lista": [
                palabra.strip().lower()
                for palabra in palabras_limpias.split(",")
                if palabra.strip()
            ]
        }

        guardar_perfil(
            nuevo_perfil,
            ventana
        )

    tk.Button(
        frame_botones,
        text="Guardar perfil",
        command=guardar
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        frame_botones,
        text="Cancelar",
        command=ventana.destroy
    ).grid(row=0, column=1, padx=10)

    tk.Button(
        frame_botones,
        text="Información",
        command=mostrar_info_perfil
    ).grid(row=0, column=2, padx=10)


    mostrar_otro()
    mostrar_sugerencia_idioma()

    return ventana


def inicializar_perfil(root):
    """
    Inicializa el perfil docente requerido por el agente inteligente.

    Parámetros:
        root (tk.Tk): Ventana principal de la aplicación.

    Retorna:
        dict | None:
            Devuelve el perfil docente cuando la configuración se encuentra
            disponible. Si el usuario no completa la configuración, devuelve
            None.

    Esta función verifica la existencia de un perfil previamente almacenado.
    Cuando no existe, muestra la ventana de configuración para que el docente
    registre su información antes de continuar con la ejecución del sistema.
    """

    perfil = cargar_perfil()

    if not perfil:

        ventana = ventana_perfil_docente(root)
        root.wait_window(ventana)

        perfil = cargar_perfil()

    if not perfil:
        return None

   
    return perfil
