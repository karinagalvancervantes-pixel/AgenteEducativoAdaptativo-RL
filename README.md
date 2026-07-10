# AgenteEducativoAdaptativo-RL

**Adaptive Intelligent Agent based on Reinforcement Learning for Educational Video Recommendation**

Prototipo de un agente inteligente adaptativo basado en Q-learning para la selección asistida de recursos audiovisuales educativos en YouTube dirigidos a docentes universitarios.

---

## Descripción

**AgenteEducativoAdaptativo-RL** es un prototipo desarrollado como parte de una investigación doctoral orientada al diseño de un agente inteligente adaptativo que apoya a docentes universitarios en la selección de videos educativos disponibles en YouTube.

El sistema utiliza la **YouTube Data API v3** para recuperar videos relacionados con una consulta temática y aplica un mecanismo de aprendizaje por refuerzo basado en **Q-Learning** para adaptar progresivamente la priorización de las recomendaciones a partir de la retroalimentación proporcionada por cada docente.

A diferencia de los sistemas tradicionales de recomendación centrados únicamente en métricas de interacción, este prototipo incorpora criterios pedagógicos y un enfoque **Human-in-the-Loop**, donde la evaluación realizada por el docente constituye la fuente principal del proceso de aprendizaje del agente.

---

# Objetivo

El objetivo de este prototipo es desarrollar un agente inteligente adaptativo que apoye la selección asistida de recursos audiovisuales educativos en YouTube mediante la integración de:

- Aprendizaje por refuerzo (Q-Learning).
- Perfil docente.
- Retroalimentación humana (Human-in-the-Loop).
- Criterios pedagógicos derivados de la literatura científica.

---

# Características principales

- Recuperación inicial de recursos educativos
- Filtrado inicial basado en contenido
- Construcción del estado
- Cálculo de recompensas
- Aprendizaje mediante Q-Learning
- Actualización del perfil adaptativo

---

# Arquitectura general

El prototipo se organiza en tres capas funcionales:

- **Presentación**
  - Interfaz gráfica.
  - Configuración del perfil.
  - Evaluación docente.

- **Procesamiento**
  - Construcción del estado.
  - Cálculo de recompensas.
  - Aprendizaje mediante Q-Learning.
  - Actualización del perfil adaptativo.

- **Datos y servicios**
  - YouTube Data API v3.
  - Persistencia en archivos JSON.

---

# Tecnologías utilizadas

- Python 3.12
- Tkinter
- YouTube Data API v3
- Requests
- JSON

---

# Requisitos

- Python 3.12 o superior.
- Conexión a Internet.
- Clave válida de YouTube Data API v3.

---

# Instalación

Clone el repositorio:

```bash
git clone https://github.com/karinagalvancervantes-pixel/AgenteEducativoAdaptativo-RL.git
```

Acceda al directorio del proyecto:

```bash
cd AgenteEducativoAdaptativo-RL
```

Instale las dependencias:

```bash
pip install -r requirements.txt
```

---

# Configuración inicial

Al ejecutar el sistema por primera vez será necesario registrar una clave válida de la **YouTube Data API v3**.

Por motivos de seguridad, el repositorio **no distribuye claves API**.

Cada usuario deberá generar y registrar su propia clave.

Una vez validada la API, el sistema solicitará la configuración inicial del perfil docente.

Durante la primera ejecución también se crearán automáticamente las carpetas config y data, donde el sistema almacenará localmente la configuración y el conocimiento adquirido por el agente.

---

# Ejecución

Ejecute:

```bash
python main.py
```

---

# Funcionamiento general

El flujo general del agente es el siguiente:

1. Configuración de la API.
2. Registro del perfil docente.
3. Recuperación de recursos audiovisuales.
4. Evaluación realizada por el docente.
5. Cálculo de recompensas.
6. Actualización de la Q-table.
7. Reconstrucción del perfil adaptativo.
8. Priorización de futuras recomendaciones.

---

# Persistencia del aprendizaje

El agente **no incorpora conocimiento previo**.

Cada docente genera su propio proceso de aprendizaje.

Durante el uso del sistema se crean automáticamente archivos de persistencia, entre ellos:

- `config_api.json`
- `perfil_docente.json`
- `historial_evaluaciones.json`
- `q_table.json`

Estos archivos **no forman parte del repositorio**, ya que representan el conocimiento adquirido por el agente durante la interacción con cada docente.

---

# Limitaciones

La versión actual del prototipo presenta las siguientes limitaciones:

- Utiliza exclusivamente la YouTube Data API v3 como fuente de recursos audiovisuales.
- El aprendizaje se realiza localmente mediante archivos JSON.
- La adaptación depende de la retroalimentación proporcionada por el docente.
- No reemplaza el criterio pedagógico del usuario; únicamente proporciona apoyo para la selección asistida de recursos.

---

# Estado del proyecto

Versión correspondiente al prototipo desarrollado como parte de una investigación doctoral.

Actualmente el sistema se encuentra en fase de verificación funcional preliminar.

---

# Investigación asociada

Este repositorio acompaña la investigación doctoral titulada:

"Agente inteligente adaptativo basado en aprendizaje por refuerzo para la personalización de videos educativos de YouTube dirigidos a docentes universitarios."

La investigación fue desarrollada utilizando la metodología Design Science Research (DSR).

---

# Licencia

Este proyecto se distribuye bajo la licencia **MIT License**.

---

# Autora

**MTIC. Karina Galván Cervantes**

Doctorado en Tecnologías de la Información

---

# Cómo citar

Mientras la investigación doctoral se encuentra en proceso de conclusión, se recomienda citar este repositorio como:

> Galván Cervantes, K. (2026). *AgenteEducativoAdaptativo-RL*. GitHub.

La referencia definitiva será actualizada una vez concluida la investigación y publicada la versión final del artefacto.

---

# Aviso

Este repositorio tiene fines exclusivamente académicos y de investigación.
