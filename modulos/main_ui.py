"""
Módulo: main_ui.py

Descripción:
Gestiona la interfaz principal del agente inteligente adaptativo. Este módulo
coordina la interacción inicial con el docente, permite realizar consultas de
videos educativos, aplica el proceso de filtrado y presenta los resultados
priorizados antes de su evaluación pedagógica.

Responsabilidades:
- Mostrar la interfaz principal.
- Administrar el perfil docente.
- Recuperar recursos educativos.
- Aplicar el filtrado inicial.
- Priorizar los resultados mediante el conocimiento aprendido.
- Presentar los resultados para su evaluación.

Integración dentro del agente:
Este módulo constituye el punto de entrada de la interacción con el usuario.
Coordina el flujo entre los módulos de recuperación, filtrado,
priorización adaptativa y presentación de resultados.

Dependencias:
- tkinter
- perfil_docente
- youtube_api
- filtro
- agente_rl
- resultados_ui

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de
videos educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""

import tkinter as tk
from tkinter import messagebox

from modulos.perfil_docente import ventana_perfil_docente, cargar_perfil
from modulos.youtube_api import buscar_videos
from modulos.resultados_ui import mostrar_resultados
from modulos.filtro import filtrar_videos
from modulos.agente_rl import (
    construir_estado,
    obtener_q_values
)


def ventana_principal(root, api_key, perfil=None):
    """
    Construye la interfaz principal del agente inteligente adaptativo.

    Desde esta ventana el docente puede realizar consultas sobre recursos
    educativos, modificar su perfil, visualizar el estado actual del
    sistema y ejecutar el proceso completo de recuperación, filtrado,
    priorización y evaluación de videos educativos.
    """

    ventana = tk.Toplevel(root)
    ventana.title("Agente Educativo Inteligente")
    ventana.geometry("500x480")
    ventana.resizable(False, False)

    #Título de la ventana principal

    tk.Label(
        ventana,
        text="Agente Educativo Inteligente",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    # Construir el panel de búsqueda de recursos educativos.

    frame_busqueda = tk.LabelFrame(ventana, text="Búsqueda de contenido", padx=10, pady=10)
    frame_busqueda.pack(fill="x", padx=20, pady=10)

    tk.Label(frame_busqueda, text="Ingrese el tema o recurso a buscar").pack()

    entrada_busqueda = tk.Entry(frame_busqueda, width=40)
    entrada_busqueda.pack(pady=5)

    subtitulos_var = tk.BooleanVar()

    tk.Checkbutton(
        frame_busqueda,
        text="Incluir solo videos con subtítulos",
        variable=subtitulos_var
    ).pack(pady=5)

    # Construir el panel de estado del sistema.

    frame_estado = tk.LabelFrame(ventana, text="Estado del sistema", padx=10, pady=10)
    frame_estado.pack(fill="x", padx=20, pady=10)

    # Mostrar la información general del perfil actualmente cargado.
    
    label_api = tk.Label(frame_estado)
    label_api.pack(anchor="w")

    label_area = tk.Label(frame_estado)
    label_area.pack(anchor="w")

    label_idioma = tk.Label(frame_estado)
    label_idioma.pack(anchor="w")

    # Mostrar las palabras clave configuradas para enriquecer las búsquedas.
    
    label_keywords = tk.Label(frame_estado)
    label_keywords.pack(anchor="w")

    def actualizar_estado():
        """
        Actualiza la información mostrada en el panel de estado a partir
        del perfil docente almacenado de forma persistente.
        """
        perfil_actual = cargar_perfil()

        if not perfil_actual:
            return

        label_api.config(text=f"API configurada: {'Sí' if api_key else 'No'}")
        label_area.config(text=f"Área del perfil: {perfil_actual['perfil_inicial'].get('area', 'N/A')}")
        label_idioma.config(text=f"Idioma: {perfil_actual['perfil_inicial'].get('idioma', 'N/A')}")

        palabras_clave = perfil_actual[
            "perfil_inicial"
        ].get(
            "palabras_clave",
            ""
        )

        if not palabras_clave:
            palabras_clave = "Ninguna"

        label_keywords.config(
            text=f"Palabras clave: {palabras_clave}"
        )

    actualizar_estado()


    def calcular_prioridad(video):
        """
        Calcula la prioridad de un recurso educativo combinando el
        conocimiento aprendido mediante Q-Learning, el puntaje obtenido
        durante el filtrado y la información almacenada en el perfil
        adaptativo del docente.
        """

        # Recuperar la versión más reciente del perfil persistente.
        perfil_actual = cargar_perfil()

        if not perfil_actual:
            return 0

        area = perfil_actual["perfil_inicial"].get("area", "general")


        # Construir el estado utilizando la representación del agente.

        estado = construir_estado(
            video,
            perfil_actual
        )

        # Recuperar los valores Q asociados al estado construido.

        q_values = obtener_q_values(estado)

        q = q_values.get("util", 0)

        q_no_util = q_values.get("no_util", 0)

        bonus = 0

        # Calcular la penalización asociada a experiencias negativas previas.

        penalizacion = 0

        if q_no_util < 0:
            penalizacion = abs(q_no_util) * 0.7
            
        # Obtener el puntaje generado durante el proceso de filtrado inicial.

        score_filtro = video.get("score_filtro", 0)

        # Obtener las preferencias aprendidas durante las interacciones previas.

        perfil_adaptativo = perfil_actual.get("perfil_adaptativo", {})

        canal_pref = perfil_adaptativo.get("canal_preferido")

        # En futuras versiones del agente podrá incorporarse la preferencia
        # por tipo de contenido (teórico, práctico o mixto) dentro del
        # cálculo de prioridad.
        # tipo_pref = perfil_adaptativo.get("tipo_preferido")


        if canal_pref and video.get("canal") == canal_pref:
            bonus += 0.3

        titulo = video.get("titulo", "").lower()
        descripcion = video.get("descripcion", "").lower()

        # Normalizar el área disciplinar para facilitar la comparación textual.

        area_lower = area.lower()

        if area_lower in titulo:
            bonus += 0.3
        elif area_lower in descripcion:
            bonus += 0.15
        
        # Recuperar el historial para estimar la madurez del aprendizaje adaptativo.

        historial = perfil_adaptativo.get("historial", [])

        # Calcular el factor de madurez del aprendizaje adaptativo.
        peso_rl = min(len(historial) / 5, 1)

        # Integrar las diferentes fuentes de información para calcular
        # la prioridad final utilizada durante el ordenamiento inicial.

        prioridad = (
            (q * 0.6 * peso_rl) +
            (score_filtro * 0.3) +
            bonus -
            penalizacion
        )
        
        return prioridad


    def buscar():
        """
        Ejecuta el flujo completo de búsqueda de recursos educativos.

        El proceso incluye la recuperación desde la API de YouTube,
        el filtrado de resultados, la priorización mediante el agente
        adaptativo y la presentación de los recursos al docente.
        """
        consulta = entrada_busqueda.get()

        # Obtener la consulta introducida por el docente.

        if not consulta.strip():
            messagebox.showwarning("Error", "Debe ingresar un tema.")
            return

        perfil_actual = cargar_perfil()

        # Recuperar el perfil vigente para contextualizar la búsqueda.

        resultado_api = buscar_videos(api_key, perfil_actual, consulta)

        # Gestionar las posibles respuestas de error devueltas por la API.

        if isinstance(resultado_api, dict) and "error" in resultado_api:

            if resultado_api["error"] == "sin_internet":
                messagebox.showerror("Error", "No hay conexión a internet.")

            elif resultado_api["error"] == "timeout":
                messagebox.showerror("Error", "La conexión tardó demasiado. Intente nuevamente.")

            elif resultado_api["error"] == "api_error":
                messagebox.showerror("Error", "Error al conectar con el servicio.")

            elif resultado_api["error"] == "sin_resultados":
                messagebox.showinfo("Sin resultados", "No se encontraron videos para la búsqueda.")

            return

        if isinstance(resultado_api, dict):
            resultados = resultado_api.get("data", [])
        else:
            resultados = resultado_api

        # Conservar únicamente los recursos compatibles con el idioma del perfil docente.

        idioma_perfil = perfil_actual["perfil_inicial"].get("idioma", "ambos")

        if idioma_perfil in ["es", "español"]:
            resultados = [
                v for v in resultados
                if v.get("idioma") in ["es", "otro"]
            ]

        elif idioma_perfil in ["en", "inglés", "ingles"]:
            resultados = [
                v for v in resultados
                if v.get("idioma") in ["en", "otro"]
            ]

        if not resultados:
            messagebox.showwarning("Aviso", "No hay resultados en el idioma seleccionado.")
            return

        # Recuperar las preferencias seleccionadas por el docente para el filtrado.

        preferencias = {
            "subtitulos": subtitulos_var.get(),
            "consulta": consulta
        }

        resultados_filtrados = filtrar_videos(resultados, perfil_actual, preferencias)

        if not resultados_filtrados:
            messagebox.showwarning("Aviso", "No hay resultados después del filtrado.")
            return

        
        # Ordenar los recursos utilizando la prioridad calculada por el agente.

        resultados_ordenados = sorted(
            resultados_filtrados,
            key=calcular_prioridad,
            reverse=True
        )

        consulta_actual = consulta

        # Presentar los recursos priorizados para su evaluación pedagógica.

        mostrar_resultados(resultados_ordenados, perfil_actual, consulta_actual)

    # Ejecutar el proceso completo de recuperación de recursos educativos.

    tk.Button(frame_busqueda, text="Buscar", command=buscar).pack(pady=10)

    def modificar_perfil():
        """
        Permite modificar el perfil docente y actualiza automáticamente
        el estado del sistema. Si existe una búsqueda previa, ésta se
        ejecuta nuevamente utilizando el perfil actualizado.
        """

        # Abrir la ventana de edición del perfil docente.

        sub = ventana_perfil_docente(root)
        root.wait_window(sub)

        # Refrescar la información mostrada en el panel de estado.

        actualizar_estado()
        
        if entrada_busqueda.get().strip():

            # Repitir la búsqueda utilizando el nuevo perfil docente.

            buscar()
            
    # Construir el panel de acciones disponibles para el docente.
    
    frame_acciones = tk.LabelFrame(ventana, text="Opciones", padx=10, pady=10)
    frame_acciones.pack(fill="x", padx=20, pady=10)
    
    # Permitir modificar el perfil docente en cualquier momento.
    
    tk.Button(
        frame_acciones,
        text="Modificar perfil docente",
        command=modificar_perfil
    ).pack(pady=5)
