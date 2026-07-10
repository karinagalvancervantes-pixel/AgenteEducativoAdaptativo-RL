"""
Módulo: perfil_adaptativo.py

Descripción:
Reconstruye el perfil adaptativo del docente a partir del historial de
evaluaciones almacenado durante la interacción con el agente inteligente
adaptativo. Este proceso permite recalcular las preferencias aprendidas sin
depender del estado previo del perfil adaptativo.

Responsabilidades:
- Reconstruir el perfil adaptativo desde el historial de evaluaciones.
- Actualizar preferencias sobre tipos de contenido y canales.
- Calcular indicadores pedagógicos acumulados.
- Persistir nuevamente el perfil reconstruido.

Dependencias:
- json
- modulos.rutas

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de
videos educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""

import json

from modulos.rutas import (
    PERFIL_FILE,
    HISTORIAL_FILE
)

def reconstruir_perfil_adaptativo():
    """
    Reconstruye el perfil adaptativo utilizando el historial de evaluaciones
    almacenado por el agente.

    El procedimiento recalcula completamente las preferencias aprendidas,
    evitando depender del contenido previamente almacenado en el perfil
    adaptativo.
    """

    if not PERFIL_FILE.exists():
        return

    if not HISTORIAL_FILE.exists():
        return

    try:

        with open(
            PERFIL_FILE,
            "r",
            encoding="utf-8"
        ) as archivo:

            perfil = json.load(archivo)

        with open(
            HISTORIAL_FILE,
            "r",
            encoding="utf-8"
        ) as archivo:

            historial = json.load(archivo)

    except (
        OSError,
        json.JSONDecodeError
    ):
        return

    # Reinicia completamente el conocimiento adaptativo derivado.
    perfil["perfil_adaptativo"] = {}

    adaptativo = perfil["perfil_adaptativo"]

    adaptativo["contador_tipo"] = {
        "teorico": 0,
        "practico": 0,
        "mixto": 0
    }

    adaptativo["canales_preferidos"] = {}

    adaptativo["palabras_emergentes"] = {}

    adaptativo["acumulado_pedagogico"] = {
        "claridad": 0.0,
        "organizacion": 0.0,
        "alineacion": 0.0,
        "conteo": 0
    }

    # Procesa todas las evaluaciones registradas.
    for evaluacion in historial:

        decision = evaluacion.get("decision")

        claridad = float(
            evaluacion.get("claridad", 0)
        )

        organizacion = float(
            evaluacion.get("organizacion", 0)
        )

        alineacion = float(
            evaluacion.get("alineacion", 0)
        )

        canal = evaluacion.get(
            "canal",
            ""
        ).strip()

        tipo_contenido = evaluacion.get("tipo_contenido")

        palabras_video = evaluacion.get(
            "palabras_clave_lista",
            []
        )

        if decision == "✔ Útil":

            if tipo_contenido in adaptativo["contador_tipo"]:
                adaptativo["contador_tipo"][tipo_contenido] += 1

            if canal:
                adaptativo["canales_preferidos"].setdefault(
                    canal,
                    0
                )
                adaptativo["canales_preferidos"][canal] += 1

            acumulado = adaptativo["acumulado_pedagogico"]

            acumulado["claridad"] += claridad
            acumulado["organizacion"] += organizacion
            acumulado["alineacion"] += alineacion
            acumulado["conteo"] += 1

            for palabra in palabras_video:

                adaptativo["palabras_emergentes"].setdefault(
                    palabra,
                    0
                )

                adaptativo["palabras_emergentes"][palabra] += 1

        elif decision == "✖ No útil":

            if canal in adaptativo["canales_preferidos"]:

                adaptativo["canales_preferidos"][canal] -= 1

                if adaptativo["canales_preferidos"][canal] < -5:

                    adaptativo["canales_preferidos"][canal] = -5

    contador = adaptativo["contador_tipo"]

    if any(contador.values()):
        adaptativo["tipo_preferido"] = max(
            contador,
            key=contador.get
        )

    canales_validos = {
        canal: frecuencia
        for canal, frecuencia
        in adaptativo["canales_preferidos"].items()
        if frecuencia > 0
    }

    if canales_validos:
        adaptativo["canal_preferido"] = max(
            canales_validos,
            key=canales_validos.get
        )

    acumulado = adaptativo["acumulado_pedagogico"]

    if acumulado["conteo"] > 0:

        adaptativo["promedios_pedagogicos"] = {
            "claridad": round(
                acumulado["claridad"] / acumulado["conteo"],
                2
            ),
            "organizacion": round(
                acumulado["organizacion"] / acumulado["conteo"],
                2
            ),
            "alineacion": round(
                acumulado["alineacion"] / acumulado["conteo"],
                2
            )
        }

    try:

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

    except OSError:
        return
