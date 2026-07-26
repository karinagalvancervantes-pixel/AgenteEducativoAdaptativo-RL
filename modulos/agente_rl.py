"""
Módulo: agente_rl.py

Descripción:
Implementa el mecanismo de aprendizaje adaptativo del agente,
basado en aprendizaje por refuerzo mediante una regla de
actualización incremental para pares estado-acción.

Responsabilidades:
- Construir la representación del estado.
- Gestionar la persistencia de la Q-table.
- Actualizar la Q-table.
- Consultar valores Q.
- Reconstruir la Q-table desde el historial.

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
from modulos.rutas import Q_TABLE_FILE

ACCIONES = (
    "util",
    "no_util"
)


def construir_estado(video, perfil):
    """
    Construye la representación del estado utilizada por el agente.

    El estado integra información del recurso educativo y del perfil
    del docente para representar el contexto de aprendizaje sobre el
    cual se actualizarán los valores Q.
    """

    perfil_inicial = perfil.get(
        "perfil_inicial",
        {}
    )

    idioma = video.get(
        "idioma",
        "otro"
    )

    duracion = video.get(
        "duracion_cat",
        "media"
    )

    tipo_canal = video.get(
        "tipo_canal",
        "general"
    )

    tipo_preferido = perfil.get(
        "perfil_adaptativo",
        {}
    ).get(
        "tipo_preferido",
        "ninguno"
    )

    area = perfil_inicial.get(
        "area",
        "general"
    )

    estado = (
        f"{idioma}|"
        f"{duracion}|"
        f"{tipo_canal}|"
        f"{tipo_preferido}|"
        f"{area}"
    )

    return estado


def cargar_q_table():
    """
    Recupera la Q-table almacenada localmente.

    Si el archivo no existe o presenta algún problema de lectura,
    devuelve una tabla vacía.
    """

    if Q_TABLE_FILE.exists():

        try:

            with open(
                Q_TABLE_FILE,
                "r",
                encoding="utf-8"
            ) as archivo:

                return json.load(archivo)

        except (
            OSError,
            json.JSONDecodeError
        ):

            return {}

    return {}


def guardar_q_table(q_table):
    """
    Guarda la Q-table actualizada en almacenamiento local.
    """

    with open(
        Q_TABLE_FILE,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            q_table,
            archivo,
            indent=4,
            ensure_ascii=False
        )


def actualizar_q_table(
    estado,
    accion,
    recompensa,
    alpha=0.1
):
    """
    Actualiza la Q-table mediante una regla de aprendizaje
    incremental de un solo paso para el par estado-acción.
    """

    q_table = cargar_q_table()

    estado = str(estado)

    # Inicializa un nuevo estado cuando aún no existe.

    if estado not in q_table:

        q_table[estado] = {
            accion: 0.0
            for accion in ACCIONES
        }

    valor_actual = q_table[estado][accion]

    # Regla de aprendizaje de un solo paso.
    # Cada evaluación docente actualiza directamente el valor
    # asociado al par estado-acción, sin utilizar bootstrap
    # sobre un estado sucesor.
    
    nuevo_valor = valor_actual + alpha * (
        recompensa
        - valor_actual
    )

    q_table[estado][accion] = round(
        nuevo_valor,
        4
    )

    guardar_q_table(q_table)


def obtener_q_values(estado):
    """
    Obtiene todos los valores Q asociados a un estado.
    """

    q_table = cargar_q_table()

    estado = str(estado)

    if estado not in q_table:

        return {
            accion: 0.0
            for accion in ACCIONES
        }

    return q_table[estado]


def obtener_valor_q(
    estado,
    accion
):
    """
    Obtiene el valor Q asociado a una acción específica.
    """

    q_values = obtener_q_values(estado)

    return q_values.get(
        accion,
        0.0
    )


def reconstruir_q_table(
    historial,
    alpha=0.1,
):
    """
    Reconstruye completamente la Q-table a partir del historial
    de evaluaciones almacenado.

    Esta función se utiliza cuando se eliminan registros del
    historial y es necesario recalcular el conocimiento aprendido
    por el agente.

    La reconstrucción aplica la misma regla de aprendizaje
    incremental utilizada por actualizar_q_table(), garantizando
    que los valores reconstruidos sean consistentes con el
    aprendizaje acumulado del agente.
    """

    q_table = {}

    for registro in historial:

        estado = registro.get("estado")
        accion = registro.get("accion")
        recompensa = registro.get("recompensa")

        if not estado or accion not in ACCIONES:
            continue

        estado = str(estado)

        # Inicializa el estado cuando aún no existe.

        if estado not in q_table:

            q_table[estado] = {
                accion: 0.0
                for accion in ACCIONES
            }

        valor_actual = q_table[estado][accion]

        nuevo_valor = valor_actual + alpha * (
            recompensa
            - valor_actual
        )

        q_table[estado][accion] = round(
            nuevo_valor,
            4
        )

    guardar_q_table(q_table)

    return q_table
