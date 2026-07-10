"""
Módulo: normalizacion.py

Descripción:
Proporciona funciones de normalización para las consultas realizadas por
el docente antes de ser utilizadas por el agente. La normalización
garantiza un formato uniforme de almacenamiento y comparación,
preservando la consistencia del historial de aprendizaje.

Responsabilidades:
- Normalizar consultas de búsqueda.
- Uniformar el formato de las consultas.
- Favorecer la consistencia del historial de aprendizaje.

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de
videos educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""


def normalizar_consulta(consulta):
    """
    Normaliza la consulta realizada por el docente.

    Convierte el texto a minúsculas y elimina espacios al inicio y al
    final para mantener un formato uniforme durante el almacenamiento y
    comparación de las consultas.
    """

    if not consulta:
        return ""

    return consulta.lower().strip()
