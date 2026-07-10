"""
Módulo: resultados_ui.py

Descripción:
Implementa la interfaz gráfica encargada de presentar los recursos
educativos recuperados por el agente inteligente adaptativo. Este módulo
permite visualizar las recomendaciones generadas, registrar la evaluación
pedagógica realizada por el docente, actualizar el aprendizaje mediante
Q-Learning y reflejar dinámicamente los cambios producidos en el proceso
de adaptación del agente.

Responsabilidades:
- Mostrar los resultados recuperados desde YouTube.
- Calcular y visualizar el nivel de recomendación adaptativa.
- Gestionar la evaluación pedagógica de los recursos educativos.
- Actualizar la Q-table mediante aprendizaje por refuerzo.
- Reconstruir el perfil adaptativo del docente.
- Actualizar dinámicamente el ranking de recomendaciones.
- Administrar la interacción entre la interfaz gráfica y los módulos del agente.

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de
videos educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""

import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from modulos.agente_rl import (
    actualizar_q_table,
    construir_estado,
    obtener_valor_q
)
from modulos.historial import (
    cargar_historial,
    guardar_historial,
    separar_resultados_por_historial
)
from modulos.perfil_adaptativo import (
    reconstruir_perfil_adaptativo
)
from modulos.recompensa import (
    calcular_recompensa
)


def normalizar(texto):
    """
    Normaliza un texto eliminando signos básicos de puntuación
    y convirtiéndolo a minúsculas.
    """

    return (
        texto.lower()
        .replace("!", "")
        .replace("?", "")
        .strip()
    )


def contar_evidencia_estado(historial, estado):
    """
    Cuenta el número de evaluaciones registradas para un mismo
    estado del agente.

    La evidencia corresponde a la cantidad de experiencias
    acumuladas para dicho estado dentro del historial.
    """

    return sum(
        1
        for registro in historial
        if registro.get("estado") == estado
    )


def calcular_recomendacion_visual(video, perfil, historial):
    """
    Calcula la representación visual del nivel de recomendación
    adaptativa para un recurso educativo.

    La recomendación se obtiene a partir del conocimiento
    aprendido por el agente mediante Q-Learning y se complementa
    con un ligero ajuste semántico cuando aún no existe
    conocimiento previo suficiente.

    Retorna:
        tuple:
            score_final, estrellas_n
    """

    estado = construir_estado(
        video,
        perfil
    )

    q_util = obtener_valor_q(
        estado,
        "util"
    ) or 0

    q_no_util = obtener_valor_q(
        estado,
        "no_util"
    ) or 0

    # Calcula el conocimiento aprendido para el estado actual.

    score_rl = q_util - abs(q_no_util)

    # Calcula un pequeño ajuste semántico cuando existen
    # coincidencias entre las palabras clave del docente y
    # el contenido del recurso.

    bonus_semantico = 0

    palabras_clave = (
        perfil["perfil_inicial"]
        .get("palabras_clave", "")
        .lower()
        .split()
    )

    texto_video = (
        f'{video.get("titulo", "")} '
        f'{video.get("descripcion", "")}'
    ).lower()

    for palabra in palabras_clave:

        if palabra in texto_video:
            bonus_semantico += 0.05

    # Determina la evidencia acumulada para el estado.

    conteo = contar_evidencia_estado(
        historial,
        estado
    )

    decision_historial = next(

        (
            registro.get("decision")

            for registro in historial

            if registro.get("video_id")
            == video.get("video_id")
        ),

        None

    )

    # Determina el nivel visual de recomendación adaptativa.
    #
    # La representación mediante estrellas depende de dos
    # condiciones:
    #
    #  *Evidencia mínima del estado (al menos tres
    #   evaluaciones).
    #
    #  *Conocimiento aprendido mediante Q-Learning,
    #   representado por:
    #
    #       score_rl = Q(util) − |Q(no_util)|
    #
    # Los umbrales fueron definidos heurísticamente durante
    # el refinamiento del artefacto y únicamente afectan la
    # representación visual mostrada al docente.

    if decision_historial == "✖ No útil":

        estrellas_n = 1

    elif conteo < 3:

        estrellas_n = 1

    else:

        if score_rl <= 0:

            estrellas_n = 1

        elif score_rl <= 0.30:

            estrellas_n = 2

        elif score_rl <= 0.60:

            estrellas_n = 3

        elif score_rl <= 0.89:

            estrellas_n = 4

        else:

            estrellas_n = 5

    # Cuando aún no existe conocimiento previo suficiente,
    # el ranking incorpora un pequeño ajuste semántico.

    if q_util == 0 and q_no_util == 0:

        score_final = score_rl + bonus_semantico

    else:

        score_final = score_rl

    return score_final, estrellas_n


def preparar_resultados(
    resultados,
    perfil,
    historial
):
    """
    Calcula la recomendación adaptativa de cada recurso,
    ordena los resultados y los separa entre pendientes
    y previamente evaluados.
    """

    resultados_ordenados = []

    for video in resultados:

        score_final, estrellas_n = calcular_recomendacion_visual(
            video,
            perfil,
            historial
        )

        video["score_rl"] = score_final
        video["estrellas_n"] = estrellas_n

        resultados_ordenados.append(video)

    resultados_ordenados.sort(
        key=lambda video: (
            video.get("estrellas_n", 1),
            video.get("score_rl", 0)
        ),
        reverse=True
    )

    return separar_resultados_por_historial(
        resultados_ordenados,
        historial
    )


def actualizar_tabla_resultados(
    tree,
    videos,
    evaluados=False
):
    """
    Actualiza el contenido de una tabla de resultados.
    """

    tree.delete(*tree.get_children())

    for video in videos:

        estrellas = "★" * video.get(
            "estrellas_n",
            1
        )

        fila = (
            video.get("decision", "")
            if evaluados
            else "",

            video.get("titulo"),
            video.get("canal"),
            video.get("duracion_cat"),
            video.get("interaccion"),
            estrellas
        )

        tree.insert(
            "",
            "end",
            values=fila,
            tags=(video.get("video_id"),)
        )


def mostrar_ayuda_recomendacion():
    texto = (
        "Nivel de recomendación adaptativa\n\n"

        "Las estrellas representan el nivel de recomendación adaptativa generado por el" 
        "agente inteligente a partir del conocimiento adquirido durante su proceso de aprendizaje.\n"

        "La asignación del nivel de recomendación considera dos condiciones:\n\n"

        "1. Evidencia acumulada para el estado\n"
        "  (mínimo tres evaluaciones).\n\n"

        "2. Nivel de aprendizaje obtenido mediante Q-Learning\n\n"

        "Interpretación del nivel de recomendación:\n\n"

        "★   Evidencia insuficiente o aprendizaje desfavorable.\n"

        "★★  Aprendizaje inicial.\n"

        "★★★ Aprendizaje favorable.\n"

        "★★★★ Aprendizaje consolidado.\n"

        "★★★★★ Aprendizaje altamente consolidado.\n\n"
        "Las estrellas constituyen un apoyo para la toma de decisiones"
        " del docente y no sustituyen su criterio durante la selección de recursos educativos. "       
    )

    messagebox.showinfo(
        "Nivel de recomendación adaptativa",
        texto
    )

def mostrar_resultados(resultados, perfil, consulta_actual):

    """
    Muestra los resultados recuperados por el agente y permite al
    docente evaluarlos.

    La interfaz presenta los recursos pendientes de evaluación,
    los videos previamente evaluados y actualiza dinámicamente el
    aprendizaje del agente conforme se registran nuevas
    interacciones.
    """    
    evaluaciones_temp = []
    resultados_base = resultados.copy() 
    ventana = tk.Toplevel()
    ventana.title("Evaluación de resultados")
    ventana.update_idletasks()
    ventana.geometry("1100x600")
    ventana.minsize(1100,550)
    ventana.resizable(True,True)
    
    # Crea el contenedor principal de las tablas de resultados.

    frame_tablas = tk.Frame(ventana)
    frame_tablas.pack(fill="x", padx=10, pady=10)

    columnas = (
        "decision",
        "titulo",
        "canal",
        "duracion",
        "interaccion",
        "relevancia"
    )

    # Crea el encabezado de la tabla de resultados pendientes.

    frame_titulo = tk.Frame(frame_tablas)
    frame_titulo.pack(fill="x", padx=10, pady=(5, 0))

    tk.Label(
        frame_titulo,
        text="Tabla de resultados y sugerencias",
        font=("Arial", 11, "bold")
    ).pack(side="left")

    lbl_info = tk.Label(
        frame_titulo,
        text="ⓘ ¿Cómo interpretar la recomendación?",
        fg="blue",
        cursor="hand2",
        font=("Arial", 9, "underline")
    )

    lbl_info.pack(side="right")

    lbl_info.bind(
        "<Button-1>",
        lambda evento: mostrar_ayuda_recomendacion()
    )

    # Construye la tabla donde se muestran los videos pendientes de evaluación.

    frame_tree_pendientes = tk.Frame(frame_tablas)
    frame_tree_pendientes.pack(fill="x", padx=10, pady=5)

    scroll_pendientes = tk.Scrollbar(frame_tree_pendientes)
    scroll_pendientes.pack(side="right", fill="y")

    tree_pendientes = ttk.Treeview(
        frame_tree_pendientes,
        columns=columnas,
        show="headings",
        yscrollcommand=scroll_pendientes.set
    )

    tree_pendientes.config(height=10)
    tree_pendientes.pack(side="left", fill="x", expand=True)

    scroll_pendientes.config(command=tree_pendientes.yview)

    # Crea el encabezado de la tabla de videos previamente evaluados.

    tk.Label(
        frame_tablas,
        text="Videos previamente evaluados que coinciden con la consulta actual",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=10, pady=(10, 0))

    # Construye la tabla que almacena los videos previamente evaluados.

    frame_tree_evaluados = tk.Frame(frame_tablas)
    frame_tree_evaluados.pack(fill="x", padx=10, pady=5)

    scroll_evaluados = tk.Scrollbar(frame_tree_evaluados)
    scroll_evaluados.pack(side="right", fill="y")

    tree_evaluados = ttk.Treeview(
        frame_tree_evaluados,
        columns=columnas,
        show="headings",
        yscrollcommand=scroll_evaluados.set
    )

    tree_evaluados.config(height=8)
    tree_evaluados.pack(side="left", fill="x", expand=True)

    scroll_evaluados.config(command=tree_evaluados.yview)

    # Configura los encabezados y dimensiones de ambas tablas.

    encabezados = {
        "decision": "Evaluación",
        "titulo": "Título del video",
        "canal": "Canal",
        "duracion": "Duración",
        "interaccion": "Interacción",
        "relevancia": "Recomendación"
    }

    anchos = {
        "decision": 100,
        "titulo": 330,
        "canal": 230,
        "duracion": 100,
        "interaccion": 120,
        "relevancia": 120
    }

    for col in columnas:
        tree_pendientes.heading(col, text=encabezados[col])
        tree_pendientes.column(col, width=anchos[col], anchor="w")

        tree_evaluados.heading(col, text=encabezados[col])
        tree_evaluados.column(col, width=anchos[col], anchor="w")

    # Recupera el historial utilizado por el agente.

    historial = cargar_historial()

    resultados_pendientes, resultados_ya_evaluados = preparar_resultados(
        resultados,
        perfil,
        historial
    )
    # Inserta en la tabla los recursos pendientes de evaluación.

    actualizar_tabla_resultados(
        tree_pendientes,
        resultados_pendientes
    )

    # Inserta en la tabla los recursos previamente evaluados.

    actualizar_tabla_resultados(
        tree_evaluados,
        resultados_ya_evaluados,
        evaluados=True
    )


    def recalcular_y_mostrar_resultados():
        """
        Actualiza dinámicamente las tablas de resultados
        utilizando el aprendizaje más reciente del agente.
        """

        historial = cargar_historial()

        resultados_pendientes, resultados_ya_evaluados = preparar_resultados(
            resultados,
            perfil,
            historial
        )

        actualizar_tabla_resultados(
            tree_pendientes,
            resultados_pendientes
        )

        actualizar_tabla_resultados(
            tree_evaluados,
            resultados_ya_evaluados,
            evaluados=True
        )

               
    def ventana_no_util(callback_guardar):
        """
        Muestra una ventana para registrar la evaluación de un recurso
        educativo considerado como no útil.

        La evaluación permite identificar si el video corresponde al tema
        de interés y si puede ser aprovechado en el contexto de enseñanza.
        """

        ventana_no_util = tk.Toplevel()
        ventana_no_util.title("Evaluación de contenido no útil")
        ventana_no_util.geometry("300x250")
        ventana_no_util.resizable(False, False)

        # Solicita el nivel de correspondencia del video con el tema consultado.

        tk.Label(
            ventana_no_util,
            text="¿El video corresponde al tema?"
        ).pack()

        tema_var = tk.IntVar(value=1)

        tk.Radiobutton(
            ventana_no_util,
            text="Nada relacionado",
            variable=tema_var,
            value=1
        ).pack(anchor="w")

        tk.Radiobutton(
            ventana_no_util,
            text="Poco relacionado",
            variable=tema_var,
            value=2
        ).pack(anchor="w")

        tk.Radiobutton(
            ventana_no_util,
            text="Sí relacionado",
            variable=tema_var,
            value=3
        ).pack(anchor="w")

        # Solicita la utilidad potencial del recurso para la práctica docente.

        tk.Label(
            ventana_no_util,
            text="¿Te sirve para clase?"
        ).pack(pady=(10, 0))

        utilidad_var = tk.IntVar(value=1)

        tk.Radiobutton(
            ventana_no_util,
            text="No sirve",
            variable=utilidad_var,
            value=1
        ).pack(anchor="w")

        tk.Radiobutton(
            ventana_no_util,
            text="Poco útil",
            variable=utilidad_var,
            value=2
        ).pack(anchor="w")

        tk.Radiobutton(
            ventana_no_util,
            text="Sí sirve",
            variable=utilidad_var,
            value=3
        ).pack(anchor="w")

    # Guarda la evaluación y cierra la ventana.
            
        def aceptar():
            datos = {
                "tema": tema_var.get(),
                "utilidad": utilidad_var.get()
            }

            callback_guardar(datos)

            ventana_no_util.destroy()

        tk.Button(
            ventana_no_util,
            text="Aceptar",
            command=aceptar
        ).pack(pady=10)


    def obtener_video(video_id):
        """
        Recupera un video específico a partir de su identificador.
        """

        return next(
            (
                video
                for video in resultados_base
                if video.get("video_id") == video_id
            ),
            None
        )
        
  
    def marcar_util():
        """
        Registra la evaluación positiva de un recurso educativo y lo
        traslada a la tabla de videos evaluados.
        """    
        seleccion = tree_pendientes.selection()

        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione un video.")
            return

        for item_seleccionado in seleccion:

            valores = list(tree_pendientes.item(item_seleccionado, "values"))

            video_id = tree_pendientes.item(item_seleccionado, "tags")[0]

            # Solicita la evaluación pedagógica del recurso.
            datos = evaluar_pedagogicamente()

            # Almacena temporalmente la evaluación realizada.
            evaluaciones_temp.append({
                "video_id": video_id,
                "valores": valores,
                "decision": "✔ Útil",
                "penalizacion_extra": 0,
                **datos
            })
            actualizar_estado_boton()

            # Actualiza la decisión mostrada en la tabla.
            valores[0] = "✔ Útil"

            # Envia el recurso a la tabla de videos evaluados.
            tree_pendientes.delete(item_seleccionado)
            tree_evaluados.insert("", "end", values=valores, tags=(video_id,))



    def evaluar_pedagogicamente():
        """
        Solicita al docente una evaluación pedagógica del recurso educativo.

        La evaluación considera el tipo de contenido y tres criterios
        pedagógicos: claridad de la explicación, organización del contenido
        y alineación con los objetivos de aprendizaje.
        """

        ventana_eval = tk.Toplevel()
        ventana_eval.title("Evaluación pedagógica")
        ventana_eval.geometry("350x520")
        ventana_eval.resizable(False, False)

        tipo_contenido = tk.StringVar(value="mixto")

        claridad = tk.IntVar(value=2)
        organizacion = tk.IntVar(value=2)
        alineacion = tk.IntVar(value=2)

        def cerrar():
            """Cierra la ventana de evaluación pedagógica."""
            ventana_eval.destroy()


        # Selecciona el tipo de contenido predominante del recurso.

        tk.Label(
            ventana_eval,
            text="Tipo de contenido",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        tk.Radiobutton(
            ventana_eval,
            text="Teórico",
            variable=tipo_contenido,
            value="teorico"
        ).pack()

        tk.Radiobutton(
            ventana_eval,
            text="Práctico",
            variable=tipo_contenido,
            value="practico"
        ).pack()

        tk.Radiobutton(
            ventana_eval,
            text="Mixto",
            variable=tipo_contenido,
            value="mixto"
        ).pack()

        tk.Label(
            ventana_eval,
            text=(
                "Escala de evaluación\n\n"
                "1 = Bajo/Confuso\n"
                "2 = Medio/ Aceptable\n"
                "3 = Alto/Entendible"
            ),
            font=("Arial", 8, "italic")
        ).pack(pady=10)

        # Evalúa la claridad de la explicación presentada en el video.

        tk.Label(
            ventana_eval,
            text=(
                "Claridad de la explicación\n"
                "(¿Se entiende fácilmente el contenido?)"
            )
        ).pack()

        tk.Scale(
            ventana_eval,
            from_=1,
            to=3,
            orient="horizontal",
            variable=claridad
        ).pack()

        # Evalúa la organización y estructura del recurso.

        tk.Label(
            ventana_eval,
            text=(
                "Organización del contenido\n"
                "(¿La información sigue un orden lógico\n"
                "y está bien estructurada?)"
            )
        ).pack()

        tk.Scale(
            ventana_eval,
            from_=1,
            to=3,
            orient="horizontal",
            variable=organizacion
        ).pack()

        # Evalúa la alineación del recurso con los objetivos de aprendizaje.

        tk.Label(
            ventana_eval,
            text=(
                "Alineación con los objetivos de aprendizaje\n"
                "(¿El contenido es útil para lo que necesitas enseñar?)"
            )
        ).pack()

        tk.Scale(
            ventana_eval,
            from_=1,
            to=3,
            orient="horizontal",
            variable=alineacion
        ).pack()

        tk.Button(
            ventana_eval,
            text="Aceptar",
            command=cerrar
        ).pack(pady=10)

        ventana_eval.protocol(
            "WM_DELETE_WINDOW",
            cerrar
        )

        ventana_eval.grab_set()
        ventana_eval.wait_window()

        return {
            "tipo_contenido": tipo_contenido.get(),
            "claridad": claridad.get(),
            "organizacion": organizacion.get(),
            "alineacion": alineacion.get()
        }


    def marcar_no_util():
        """
        Registra una evaluación negativa del recurso educativo y solicita
        información adicional para calcular la penalización aplicada al
        aprendizaje del agente.
        """

        seleccion = tree_pendientes.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un video."
            )
            return

        item_seleccionado = seleccion[0]

        video_id_seleccionado = tree_pendientes.item(
            item_seleccionado,
            "tags"
        )[0]

        def guardar_evaluacion(datos_extra):
            """
            Calcula la penalización asociada a la evaluación negativa y
            registra temporalmente la decisión del docente.
            """

            penalizacion = 0

            # Penaliza cuando el recurso presenta baja relación con el tema.

            if datos_extra["tema"] == 1:
                penalizacion -= 1.5
            elif datos_extra["tema"] == 2:
                penalizacion -= 0.7

            # Penaliza cuando el recurso tiene poca utilidad docente.

            if datos_extra["utilidad"] == 1:
                penalizacion -= 0.7
            elif datos_extra["utilidad"] == 2:
                penalizacion -= 0.3

            decision = "✖ No útil"

            valores = list(
                tree_pendientes.item(
                    item_seleccionado,
                    "values"
                )
            )

            valores[0] = decision

            tree_evaluados.insert(
                "",
                "end",
                values=valores,
                tags=(video_id_seleccionado,)
            )

            tree_pendientes.delete(
                item_seleccionado
            )

            # Almacena temporalmente la evaluación realizada.

            evaluaciones_temp.append({
                "video_id": video_id_seleccionado,
                "valores": valores,
                "decision": decision,
                "penalizacion_extra": penalizacion
            })

            actualizar_estado_boton()

        ventana_no_util(
            guardar_evaluacion
        )

        
    def confirmar():

        """
        Confirma las evaluaciones realizadas durante la sesión, calcula las
        recompensas correspondientes, actualiza el aprendizaje del agente y
        reconstruye el perfil adaptativo.
        """
            
        btn_confirmar.config(state="disabled") 
        historial = cargar_historial()
        ids_historial = {
            (h["video_id"], h.get("consulta"))
            for h in historial
        }

        nuevas_evaluaciones = []
        temp_dict = {t["video_id"]: t for t in evaluaciones_temp}
                   
        for item in tree_evaluados.get_children():

            valores = tree_evaluados.item(item, "values")

            video_id = tree_evaluados.item(item, "tags")[0]

            video = obtener_video(video_id)    

            if not video:
                continue

            # Evita registrar nuevamente videos previamente aprendidos.

            if (video["video_id"], consulta_actual) in ids_historial:
                continue

            evaluacion_temporal = temp_dict.get(
                video_id,
                {}
            )

            if not evaluacion_temporal:
                continue

            nuevas_evaluaciones.append({
                "video_id": video["video_id"],
                "titulo": video.get("titulo"),
                "canal": video.get("canal"),
                "consulta": consulta_actual,
                "area": perfil["perfil_inicial"].get("area"),
                "decision": valores[0],
                "duracion_cat": video.get("duracion_cat"),
                "interaccion": video.get("interaccion"),
                "idioma": video.get("idioma"),
                "tipo_canal": video.get("tipo_canal"),

                # Conserva la evaluación pedagógica para actualizar el aprendizaje
                # y reconstruir el perfil adaptativo.
                "tipo_contenido": evaluacion_temporal.get("tipo_contenido"),
                "claridad": evaluacion_temporal.get("claridad", 0),
                "organizacion": evaluacion_temporal.get("organizacion", 0),
                "alineacion": evaluacion_temporal.get("alineacion", 0),
            })

        if not nuevas_evaluaciones:

            messagebox.showinfo(
                "Aviso",
                "No hay nuevos videos para aprendizaje."
            )

            return
            
        # Incorpora la penalización derivada de las evaluaciones negativas.

        for evaluacion in nuevas_evaluaciones:

            evaluacion["penalizacion_extra"] = (
                temp_dict.get(
                    evaluacion["video_id"],
                    {}
                ).get(
                    "penalizacion_extra",
                    0
                )
            )

        recompensas = calcular_recompensa(
            nuevas_evaluaciones,
            perfil
        )

        for evaluacion, recompensa_calculada in zip(
            nuevas_evaluaciones,
            recompensas
        ):

            estado = construir_estado(
                evaluacion,
                perfil
            )

            accion = (
                "util"
                if "Útil" in evaluacion["decision"]
                else "no_util"
            )

            recompensa = recompensa_calculada["recompensa"]

            # Registra la información necesaria para reconstruir el aprendizaje.

            evaluacion["estado"] = estado
            evaluacion["accion"] = accion
            evaluacion["recompensa"] = recompensa

            # Actualiza la Q-table del agente.

            actualizar_q_table(
                estado,
                accion,
                recompensa
            )

        # Persiste el aprendizaje y reconstruye el perfil adaptativo.

        guardar_historial(
            nuevas_evaluaciones
        )

        reconstruir_perfil_adaptativo()

        evaluaciones_temp.clear()

        recalcular_y_mostrar_resultados()

        messagebox.showinfo(
            "Evaluación",
            "Evaluación registrada correctamente.\n"
            "Las recomendaciones han sido actualizadas."
        )
    

    def deshacer_evaluacion():
        """
        Revierte una evaluación realizada durante la sesión actual y
        devuelve el recurso a la tabla de pendientes.
        """

        for item in tree_evaluados.selection():

            valores = list(
                tree_evaluados.item(
                    item,
                    "values"
                )
            )

            video_id = tree_evaluados.item(
                item,
                "tags"
            )[0]

            # Verifica que la evaluación pertenezca a la sesión actual.

            fue_evaluado_en_sesion = any(
                evaluacion["video_id"] == video_id
                for evaluacion in evaluaciones_temp
            )

            if not fue_evaluado_en_sesion:

                messagebox.showwarning(
                    "Aviso",
                    "Este video ya estaba evaluado en el historial "
                    "y no puede regresar a pendientes."
                )

                continue

            # Elimina la marca de evaluación del recurso.

            valores[0] = ""

            # Retira el recurso de la tabla de evaluados.

            tree_evaluados.delete(item)

            # Restituye el recurso a la tabla de pendientes.

            tree_pendientes.insert(
                "",
                "end",
                values=valores,
                tags=(video_id,)
            )

            # Elimina la evaluación temporal almacenada durante la sesión.

            evaluaciones_temp[:] = [
                evaluacion
                for evaluacion in evaluaciones_temp
                if evaluacion["video_id"] != video_id
            ]

            actualizar_estado_boton()


    def ver_video():
        """
        Abre en el navegador el recurso educativo seleccionado por el
        docente, tanto de la tabla de pendientes como de la tabla de
        videos previamente evaluados.
        """

        # Primero intenta obtener la selección de la tabla superior.
        seleccion = tree_pendientes.selection()
        tree_origen = tree_pendientes

        # Si no hay selección, intenta con la tabla inferior.
        if not seleccion:
            seleccion = tree_evaluados.selection()
            tree_origen = tree_evaluados

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un video."
            )
            return

        item_seleccionado = seleccion[0]

        video_id = tree_origen.item(
            item_seleccionado,
            "tags"
        )[0]

        video = obtener_video(video_id)

        if video and video.get("url"):

            webbrowser.open(
                video.get("url")
            )

        else:

            messagebox.showerror(
                "Error",
                "No se pudo abrir el video."
            )


    # Construye el panel de acciones disponible para el docente.

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=15)

    contenedor_botones = tk.Frame(frame_botones)
    contenedor_botones.pack(anchor="center")

    tk.Button(
        contenedor_botones,
        text="Ver video",
        command=ver_video
    ).pack(side="left", padx=5)

    tk.Button(
        contenedor_botones,
        text="✔ Útil",
        command=marcar_util
    ).pack(side="left", padx=5)

    tk.Button(
        contenedor_botones,
        text="✖ No útil",
        command=marcar_no_util
    ).pack(side="left", padx=5)

    tk.Button(
        contenedor_botones,
        text="↩ Deshacer previo aprendizaje",
        command=deshacer_evaluacion
    ).pack(side="left", padx=5)

    btn_confirmar = tk.Button(
        contenedor_botones,
        text="Confirmar evaluación",
        command=confirmar
    )

    btn_confirmar.pack(
        side="left",
        padx=5
    )

    btn_confirmar.config(
        state="disabled"
    )


    def actualizar_estado_boton():
        """
        Habilita o deshabilita el botón de confirmación según existan
        evaluaciones pendientes por registrar.
        """

        if evaluaciones_temp:
            btn_confirmar.config(state="normal")
        else:
            btn_confirmar.config(state="disabled")


    actualizar_estado_boton()
