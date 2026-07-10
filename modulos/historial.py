"""
Módulo: historial.py

Descripción:
Gestiona la persistencia del historial de evaluaciones realizadas por el
docente. Este módulo permite almacenar, recuperar, organizar y eliminar
las evaluaciones registradas, garantizando la consistencia del proceso de
aprendizaje adaptativo y la reconstrucción del conocimiento adquirido por
el agente.

Responsabilidades:
- Cargar el historial de evaluaciones.
- Guardar nuevas evaluaciones.
- Separar recursos pendientes y previamente evaluados.
- Eliminar evaluaciones del historial.
- Reconstruir la Q-table después de eliminar evaluaciones.

Dependencias:
- json
- modulos.rutas
- modulos.normalizacion
- modulos.agente_rl

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de
videos educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""

import json
from modulos.normalizacion import normalizar_consulta
from modulos.agente_rl import reconstruir_q_table

from modulos.rutas import HISTORIAL_FILE

def cargar_historial():
    """
    Recupera el historial de evaluaciones almacenado localmente.

    Si el archivo no existe o su contenido no puede interpretarse
    como JSON válido, se devuelve una lista vacía.
    """

    if not HISTORIAL_FILE.exists():
        return []

    try:

        with open(
            HISTORIAL_FILE,
            "r",
            encoding="utf-8"
        ) as archivo:

            return json.load(archivo)

    except (
        OSError,
        json.JSONDecodeError
    ):
        return []


def guardar_historial(nuevos_registros):
    """
    Almacena nuevas evaluaciones en el historial del agente.

    Antes de registrar cada evaluación, verifica que no exista una
    combinación previa del mismo video y la misma consulta, evitando
    duplicados y preservando la consistencia del historial.
    """

    historial = cargar_historial()

    # Construye el índice de evaluaciones previamente almacenadas.

    existentes = {
        (
            registro["video_id"],
            normalizar_consulta(
                registro.get("consulta", "")
            )
        )
        for registro in historial
    }

    for nuevo in nuevos_registros:

        clave = (
            nuevo["video_id"],
            normalizar_consulta(
                nuevo.get("consulta", "")
            )
        )

        if clave not in existentes:
            historial.append(nuevo)

    # Guarda el historial actualizado.

    with open(
        HISTORIAL_FILE,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            historial,
            archivo,
            indent=4,
            ensure_ascii=False
        )
        

def separar_resultados_por_historial(resultados, historial):
    """
    Separa los recursos recuperados en videos pendientes de evaluación y
    videos previamente evaluados.

    La clasificación se realiza utilizando el identificador único del
    recurso (video_id). Cuando un video ya existe en el historial, se
    recupera la información de la evaluación previamente almacenada para
    mantener la consistencia de la interfaz y del proceso adaptativo.
    """

    # Recupera los identificadores de videos previamente evaluados.

    ids_evaluados = {
        item.get("video_id")
        for item in historial
        if item.get("video_id")
    }

    pendientes = []
    evaluados = []

    for video in resultados:

        video_id = video.get("video_id")

        if video_id in ids_evaluados:

            # Recupera la evaluación previamente almacenada.

            evaluacion_previa = next(
                (
                    item
                    for item in historial
                    if item.get("video_id") == video_id
                ),
                None
            )

            if evaluacion_previa:

                # Conserva la información de la evaluación previa para
                # mostrarla nuevamente en la interfaz.

                video["decision"] = evaluacion_previa.get(
                    "decision",
                    "Evaluado"
                )

                video["claridad"] = evaluacion_previa.get(
                    "claridad",
                    0
                )

                video["organizacion"] = evaluacion_previa.get(
                    "organizacion",
                    0
                )

                video["alineacion"] = evaluacion_previa.get(
                    "alineacion",
                    0
                )

                video["consulta_previa"] = evaluacion_previa.get(
                    "consulta",
                    ""
                )

                video["ya_evaluado"] = True

            evaluados.append(video)

        else:

            video["ya_evaluado"] = False
            pendientes.append(video)

    return pendientes, evaluados


def eliminar_evaluacion(video_id, consulta=None):
    """
    Elimina una evaluación del historial y reconstruye el aprendizaje
    del agente.

    La eliminación puede realizarse para una consulta específica o para
    todas las evaluaciones asociadas al mismo video. Una vez actualizado
    el historial, la Q-table se reconstruye completamente para mantener
    la consistencia del conocimiento aprendido.
    """

    historial = cargar_historial()

    nuevo_historial = []

    for item in historial:

        if consulta:

            if not (
                item["video_id"] == video_id
                and item.get("consulta") == consulta
            ):
                nuevo_historial.append(item)

        else:

            if item["video_id"] != video_id:
                nuevo_historial.append(item)

    with open(
        HISTORIAL_FILE,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            nuevo_historial,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    # Reconstruye la Q-table para mantener la consistencia del aprendizaje.

    reconstruir_q_table(nuevo_historial)

    return nuevo_historial
