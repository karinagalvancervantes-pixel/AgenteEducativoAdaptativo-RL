"""
Módulo: agente_rl.py

Descripción:
Implementa el algoritmo de aprendizaje por refuerzo basado en Q-Learning.
El agente construye estados a partir de las características del recurso
educativo y del perfil del docente, selecciona acciones mediante una
política ε-greedy y actualiza la Q-table utilizando las recompensas
obtenidas durante la interacción.

Responsabilidades:
- Construir la representación del estado.
- Gestionar la persistencia de la Q-table.
- Seleccionar acciones mediante política ε-greedy.
- Actualizar la Q-table.
- Consultar valores Q.
- Reconstruir la Q-table desde el historial.

Dependencias:
- json
- random
- modulos.rutas

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de
videos educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""

import json
import random
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


def seleccionar_accion(
    estado,
    epsilon=0.1
):
    """
    Selecciona una acción utilizando una política ε-greedy.

    Con probabilidad ε el agente explora una acción aleatoria.
    En caso contrario selecciona la acción con mayor valor Q.
    """

    q_table = cargar_q_table()

    estado = str(estado)

    # Explora cuando el estado aún no ha sido aprendido.

    if estado not in q_table:
        return random.choice(ACCIONES)

    # Explora aleatoriamente con probabilidad ε.

    if random.random() < epsilon:
        return random.choice(ACCIONES)

    # Explota el conocimiento previamente aprendido.

    valores = q_table[estado]

    return max(
        valores,
        key=valores.get
    )


def actualizar_q_table(
    estado,
    accion,
    recompensa,
    alpha=0.1,
    gamma=0.9
):
    """
    Actualiza la Q-table utilizando la ecuación de Q-Learning.
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

    # En este prototipo se utiliza un modelo simplificado donde
    # el estado futuro corresponde al mismo contexto de decisión.

    max_futuro = max(
        q_table[estado].values()
    )

    nuevo_valor = valor_actual + alpha * (
        recompensa
        + gamma * max_futuro
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
    gamma=0.9
):
    """
    Reconstruye completamente la Q-table a partir del historial
    de evaluaciones almacenado.

    Esta función se utiliza cuando se eliminan registros del
    historial y es necesario recalcular el conocimiento aprendido
    por el agente.
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

        max_futuro = max(
            q_table[estado].values()
        )

        nuevo_valor = valor_actual + alpha * (
            recompensa
            + gamma * max_futuro
            - valor_actual
        )

        q_table[estado][accion] = round(
            nuevo_valor,
            4
        )

    guardar_q_table(q_table)

    return q_table
