"""
Módulo: recompensa.py

Descripción:
Calcula la recompensa asociada a cada evaluación realizada por el docente.
La función integra criterios de preferencia del usuario, características
del recurso educativo y la valoración pedagógica registrada durante la
interacción para generar la recompensa que posteriormente será utilizada
por el algoritmo de aprendizaje por refuerzo.

Responsabilidades:
- Calcular la recompensa base a partir de la decisión del docente.
- Incorporar ajustes derivados del perfil inicial y adaptativo.
- Integrar la evaluación pedagógica del recurso educativo.
- Aplicar penalizaciones cuando el recurso sea considerado no útil.
- Limitar la recompensa al intervalo definido para el agente.

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de
videos educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""


def calcular_recompensa(evaluaciones, perfil):
    """
    Calcula la recompensa correspondiente a cada video evaluado por el
    docente.

    La recompensa considera la utilidad del recurso, las preferencias
    registradas en el perfil del docente, las características del video
    recuperado y la evaluación pedagógica realizada durante la interacción.
    """

    recompensas = []

    perfil_inicial = perfil["perfil_inicial"]
    perfil_adaptativo = perfil.get(
        "perfil_adaptativo",
        {}
    )

    duracion_pref = perfil_inicial.get(
        "duracion_preferida"
    )

    canales_preferidos = perfil_adaptativo.get(
        "canales_preferidos",
        {}
    )

    for evaluacion in evaluaciones:

        # Obtiene las características generales del video.
        duracion = evaluacion.get("duracion_cat")
        tipo_canal = evaluacion.get("tipo_canal")
        interaccion = evaluacion.get("interaccion")
        canal = evaluacion.get("canal")

        # Recupera la evaluación pedagógica registrada por el docente.
        claridad = evaluacion.get("claridad", 0)
        organizacion = evaluacion.get("organizacion", 0)
        alineacion = evaluacion.get("alineacion", 0)

        decision = evaluacion.get("decision")

        penalizacion_extra = evaluacion.get(
            "penalizacion_extra",
            0
        )

        if not decision:
            continue

        # Establece la recompensa base según la utilidad del recurso.

        if decision == "✔ Útil":
            recompensa = 1

        elif decision == "✖ No útil":
            recompensa = -1

        else:
            recompensa = 0

        ajuste = 0

        # Favorece recursos cuya duración coincide con la preferencia del docente.

        if (
            duracion_pref != "indefinido"
            and duracion == duracion_pref
        ):
            ajuste += 0.2

        # Incrementa progresivamente la recompensa de los canales
        # que el docente ha evaluado positivamente con mayor frecuencia.

        if canal in canales_preferidos:

            frecuencia = canales_preferidos[canal]

            ajuste += min(
                frecuencia * 0.05,
                0.30
            )

        # Favorece recursos provenientes de canales educativos.

        if tipo_canal == "educativo":
            ajuste += 0.2

        # Considera el nivel de interacción del video como indicador
        # complementario de aceptación por parte de los usuarios.

        if interaccion == "alta":
            ajuste += 0.2

        elif interaccion == "media":
            ajuste += 0.1

        # Incorpora la evaluación pedagógica únicamente cuando
        # el recurso fue considerado útil.

        if decision == "✔ Útil":

            claridad_n = claridad / 3
            organizacion_n = organizacion / 3
            alineacion_n = alineacion / 3

            ajuste += 0.2 * claridad_n
            ajuste += 0.2 * organizacion_n
            ajuste += 0.3 * alineacion_n

        # Calcula la recompensa final.

        if decision == "✔ Útil":

            recompensa_final = recompensa + ajuste

        elif decision == "✖ No útil":

            recompensa_final = (
                recompensa
                - ajuste
                + penalizacion_extra
            )

        else:

            recompensa_final = 0

        # Restringe la recompensa al intervalo definido para el agente.

        recompensa_final = max(
            -3.0,
            min(2.5, recompensa_final)
        )

        recompensas.append({

            "video_id": evaluacion["video_id"],

            "recompensa": round(
                recompensa_final,
                3
            )

        })

    return recompensas
