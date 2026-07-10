"""
Módulo: filtro.py

Descripción:
Implementa el filtrado y la priorización inicial de los recursos educativos
recuperados desde la API de YouTube Data v3. El módulo asigna una puntuación
a cada video considerando las preferencias declaradas por el docente, con el
propósito de priorizar los recursos más afines antes de que intervengan los
mecanismos de aprendizaje adaptativo.

Responsabilidades:
- Evaluar la correspondencia temática entre los videos recuperados y la
  consulta realizada, considerando además las preferencias declaradas por
  el docente.
- Asignar una puntuación inicial a cada recurso educativo.
- Ordenar los resultados según la puntuación obtenida.
- Limitar la cantidad de recursos entregados a los módulos posteriores.

Integración dentro del agente:
Este módulo recibe los videos recuperados por youtube_api.py y genera una
priorización inicial basada en reglas, la cual constituye el punto de partida
para el proceso de personalización implementado por el agente inteligente.

Dependencias:
Ninguna dependencia externa.

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de videos
educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""

MAX_RESULTADOS = 20


def filtrar_videos(resultados, perfil, preferencias):
    """
    Prioriza los videos recuperados de acuerdo con las preferencias del
    docente antes de iniciar el proceso de aprendizaje adaptativo.

    Parámetros:
        resultados (list): Lista de videos recuperados desde la API de
            YouTube.
        perfil (dict): Perfil docente registrado en el sistema.
        preferencias (dict): Preferencias adicionales seleccionadas durante
            la búsqueda.

    Retorna:
        list:
            Lista de videos ordenados por la puntuación obtenida durante
            el proceso de filtrado inicial.
    """

    perfil_inicial = perfil.get("perfil_inicial", {})

    duracion_pref = perfil_inicial.get(
        "duracion_preferida",
        "indefinido"
    ).lower()

    idioma_pref = perfil_inicial.get(
        "idioma",
        "ambos"
    ).lower()

    usar_subtitulos = preferencias.get(
        "subtitulos",
        False
    )

    consulta = [
        palabra
        for palabra in preferencias.get(
            "consulta",
            ""
        ).lower().split()
        if len(palabra) > 2
    ]

    # Evalúa cada recurso educativo recuperado para asignar una
    # puntuación inicial de prioridad.
    for video in resultados:

        score = 0
        # Evalúa la coincidencia entre la consulta realizada por el
        # docente y el título del recurso educativo.
        # Evalúa la coincidencia entre la consulta realizada por el
        # docente y el título del recurso educativo.

        titulo = video.get(
            "titulo",
            ""
        ).lower()

        coincidencias = sum(
            1
            for palabra in consulta
            if palabra in titulo
        )

        # Si todas las palabras significativas de la consulta
        # aparecen en el título, se prioriza el recurso por
        # considerarlo altamente pertinente.

        if (
            consulta
            and coincidencias == len(consulta)
        ):

            score += 5

        else:

            score += coincidencias
            
        duracion = video.get("duracion_cat")
        idioma_video = video.get(
            "idioma",
            ""
        ).lower()

        subtitulos = video.get(
            "subtitulos",
            False
        )

        # Evalúa la coincidencia entre el idioma del recurso y la
        # preferencia indicada por el docente.
        if idioma_pref == "español":

            if idioma_video.startswith("es"):
                score += 1

        elif idioma_pref == "inglés":

            if idioma_video.startswith("en"):
                score += 1

        elif idioma_pref == "ambos":

            score += 1

        # Evalúa la correspondencia entre la duración preferida y la
        # categoría del recurso recuperado.
        if duracion_pref == "indefinido":
            pass

        elif (
            duracion_pref == "corta"
            and duracion == "corta"
        ):
            score += 1

        elif (
            duracion_pref == "media"
            and duracion == "media"
        ):
            score += 1

        elif (
            duracion_pref == "larga"
            and duracion == "larga"
        ):
            score += 1

        # Considera la disponibilidad de subtítulos cuando el docente
        # ha indicado esta preferencia.
        if usar_subtitulos:

            if subtitulos:
                score += 1

        else:

            score += 1

        video["score_filtro"] = score

    # Ordena los recursos de acuerdo con la puntuación obtenida.
    resultados.sort(
        key=lambda video: video.get(
            "score_filtro",
            0
        ),
        reverse=True
    )

    # Limita el número de recursos entregados a los módulos posteriores.
    return resultados[:MAX_RESULTADOS]
