"""
Módulo: youtube_api.py

Descripción:
Gestiona la comunicación entre el agente inteligente adaptativo y la API de
YouTube Data v3 para recuperar información de videos educativos. Este módulo
construye las consultas, obtiene los resultados desde la API, recupera
información adicional de cada video y genera una estructura de datos lista para
ser utilizada por el proceso de recomendación.

Responsabilidades:
- Construir consultas a la API de YouTube Data v3.
- Recuperar videos de acuerdo con la consulta realizada.
- Obtener información adicional de cada video mediante una segunda consulta.
- Normalizar información relevante para el agente.
- Generar una estructura de datos homogénea para las siguientes etapas del sistema.

Integración dentro del agente:
Este módulo constituye la primera etapa del proceso de recuperación de recursos
educativos. Los resultados obtenidos son utilizados posteriormente por los
módulos de filtrado, personalización y aprendizaje adaptativo.

Dependencias:
- requests
- isodate

Contexto del artefacto:
Artefacto desarrollado como parte de la tesis doctoral "Agente inteligente
adaptativo basado en aprendizaje por refuerzo para la personalización de videos
educativos de YouTube dirigidos a docentes universitarios".

Autora:
Karina Galván Cervantes
"""

import requests
import isodate


def normalizar_idioma(codigo_idioma):
    """
    Normaliza el código de idioma recuperado desde la API de YouTube.

    Parámetros:
        codigo_idioma (str): Código de idioma asociado al video.

    Retorna:
        str:
            "es" para español, "en" para inglés y "otro" para cualquier otro
            idioma o cuando la información no está disponible.
    """

    codigo_idioma = (codigo_idioma or "").lower()

    if codigo_idioma.startswith("es"):
        return "es"

    if codigo_idioma.startswith("en"):
        return "en"

    return "otro"


def buscar_videos(api_key, perfil, consulta):
    """
    Recupera videos educativos desde la API de YouTube Data v3 a partir de
    la consulta realizada por el docente y de la información disponible en
    su perfil.

    Parámetros:
        api_key (str): API Key de YouTube Data v3.
        perfil (dict): Perfil docente utilizado para contextualizar la búsqueda.
        consulta (str): Consulta ingresada por el docente.

    Retorna:
        list | dict:
            Lista de videos recuperados cuando la consulta es exitosa o un
            diccionario con el tipo de error cuando ocurre algún problema de
            comunicación con la API.
    """

    youtube_search_url = "https://www.googleapis.com/youtube/v3/search"

    # Recupera la información inicial del perfil docente utilizada para
    # contextualizar la consulta enviada a la API de YouTube.
    perfil_inicial = perfil.get(
        "perfil_inicial",
        {}
    )

    idioma_preferido = perfil_inicial.get(
        "idioma",
        ""
    ).lower()

    palabras_clave = perfil_inicial.get(
        "palabras_clave",
        ""
    )

    # Construye la consulta considerando las palabras clave definidas
    # en el perfil docente y preserva las consultas compuestas
    # mediante comillas para favorecer la recuperación temática.

    consulta = consulta.strip()

    if " " in consulta:

        consulta_base = f'"{consulta}"'

    else:

        consulta_base = consulta

    if palabras_clave:

        consulta_youtube = (
            f"{consulta_base} {palabras_clave}"
        )

    else:

        consulta_youtube = consulta_base

    # Determina el idioma preferido para ajustar la búsqueda.
    es_espanol = idioma_preferido in [
        "español",
        "es"
    ]

    es_ingles = idioma_preferido in [
        "inglés",
        "ingles",
        "en"
    ]

    # Cuando el idioma no corresponde exclusivamente a español o inglés,
    # no se aplica filtrado adicional.   

    params = {
        "part": "snippet",
        "q": consulta_youtube,
        "type": "video",
        "maxResults": 25,
        "key": api_key
    }

    # Incorpora el idioma preferido para orientar la recuperación de resultados.
    if es_espanol:

        params["relevanceLanguage"] = "es"

    if es_ingles:

        params["relevanceLanguage"] = "en"

    try:
        
        response = requests.get(
            youtube_search_url,
            params=params,
            timeout=15
        )

        if response.status_code != 200:
            return {"error": "api_error"}

        data = response.json()

        
    except requests.exceptions.ConnectionError:
        return {"error": "sin_internet"}

    except requests.exceptions.Timeout:
        return {"error": "timeout"}

    except requests.exceptions.RequestException:
        return {"error": "api_error"}

    
    # Almacena temporalmente la información recuperada durante la primera
    # consulta y los identificadores que serán utilizados en la consulta
    # de detalles.
    videos = []
    video_ids = []

    # Procesa los resultados obtenidos mediante la consulta de búsqueda.
    for item in data.get("items", []):

        try:

            video_id = item["id"]["videoId"]

            snippet = item["snippet"]

            codigo_idioma = (
                snippet.get("defaultAudioLanguage")
                or snippet.get("defaultLanguage")
                or ""
            )

            idioma_final = normalizar_idioma(
                codigo_idioma
            )

            # Cuando el idioma preferido es "ambos", no se aplica filtrado.

            video_ids.append(video_id)

            videos.append({

                "video_id": video_id,

                "titulo": snippet.get(
                    "title",
                    ""
                ),

                "descripcion": snippet.get(
                    "description",
                    ""
                ),

                "canal": snippet.get(
                    "channelTitle",
                    ""
                ),

                "fecha_publicacion": snippet.get(
                    "publishedAt",
                    ""
                ),

                "idioma": idioma_final
            })
            
        # Algunos recursos recuperados por la API pueden presentar
        # información incompleta o inconsistente. En esos casos se
        # omite únicamente el recurso afectado para continuar el
        # procesamiento del resto de los resultados.

        except Exception:
            # Continúa procesando los demás elementos para evitar que un
            # recurso con información incompleta interrumpa la recuperación.
            continue

    # Verifica que la primera consulta haya recuperado al menos un video.
    if not video_ids:
        return {"error": "sin_resultados"}

    youtube_details_url = (
        "https://www.googleapis.com/youtube/v3/videos"
    )

    params_detalles = {

        "part": "contentDetails,statistics,snippet",

        "id": ",".join(video_ids),

        "key": api_key
    }

    try:

        response_detalles = requests.get(
            youtube_details_url,
            params=params_detalles,
            timeout=15
        )

        if response_detalles.status_code != 200:
            return {"error": "api_error"}

        data_detalles = response_detalles.json()
    
    except requests.exceptions.ConnectionError:
        return {"error": "sin_internet"}

    except requests.exceptions.Timeout:
        return {"error": "timeout"}

    except requests.exceptions.RequestException:
        return {"error": "api_error"}

    # Construye un diccionario que concentra la información adicional de
    # cada video recuperada durante la segunda consulta.
    detalles_dict = {}

    for item in data_detalles.get("items", []):

        try:

            video_id = item["id"]

            content = item["contentDetails"]

            duracion_iso = content["duration"]

            duracion_seg = int(
                isodate.parse_duration(
                    duracion_iso
                ).total_seconds()
            )

            subtitulos = (
                content.get("caption", "false") == "true"
            )

            estadisticas = item.get(
                "statistics",
                {}
            )

            vistas = int(
                estadisticas.get("viewCount", 0)
            )

            likes = int(
                estadisticas.get("likeCount", 0)
            ) if "likeCount" in estadisticas else 0

            snippet = item.get(
                "snippet",
                {}
            )

            categoria = snippet.get(
                "categoryId",
                ""
            )

            detalles_dict[video_id] = {

                "duracion_seg": duracion_seg,

                "vistas": vistas,

                "likes": likes,

                "subtitulos": subtitulos,

                "categoria": categoria
            }

        # Algunos recursos recuperados por la API pueden presentar
        # información incompleta o inconsistente. En esos casos se
        # omite únicamente el recurso afectado para continuar el
        # procesamiento del resto de los resultados.
        
        except Exception:
            # Continúa procesando los demás elementos para evitar que un
            # recurso con información incompleta interrumpa la recuperación.
            continue

    # Integra la información recuperada durante ambas consultas para generar
    # la estructura de datos que utilizarán los módulos posteriores del agente.
    resultados_finales = []

    for video in videos:

        try:

            video_id = video["video_id"]

            detalles = detalles_dict.get(
                video_id,
                {}
            )

            duracion_seg = detalles.get(
                "duracion_seg",
                0
            )

            vistas = detalles.get(
                "vistas",
                0
            )

            likes = detalles.get(
                "likes",
                0
            )

            # Clasifica la duración del video en categorías utilizadas por
            # el proceso de personalización.
            if duracion_seg < 600:

                duracion_cat = "corta"

            elif duracion_seg < 1200:

                duracion_cat = "media"

            else:

                duracion_cat = "larga"

            # Calcula un indicador simple de interacción a partir de la
            # relación entre "Me gusta" y número de visualizaciones.
            ratio_interaccion = (
                (likes / vistas)
                if vistas > 0
                else 0
            )

            if ratio_interaccion > 0.05:

                interaccion = "alta"

            elif ratio_interaccion > 0.02:

                interaccion = "media"

            else:

                interaccion = "baja"

            # Clasifica el tipo de canal utilizando palabras clave
            # presentes en el nombre del canal.
            nombre_canal = (
                video["canal"].lower()
            )

            if any(

                palabra in nombre_canal

                for palabra in [
                    "academy",
                    "universidad",
                    "edu"
                ]
            ):

                tipo_canal = "educativo"

            else:

                tipo_canal = "general"

            resultado = {

                "video_id": video_id,

                "titulo": video["titulo"],

                "descripcion": video["descripcion"],

                "canal": video["canal"],

                "url":
                f"https://www.youtube.com/watch?v={video_id}",

                "idioma": video["idioma"],

                "fecha_publicacion":
                video["fecha_publicacion"],

                "subtitulos":
                detalles.get(
                    "subtitulos",
                    False
                ),

                "categoria":
                detalles.get(
                    "categoria",
                    ""
                ),

                "duracion_seg": duracion_seg,

                "duracion_cat": duracion_cat,

                "vistas": vistas,

                "likes": likes,

                "interaccion": interaccion,

                "tipo_canal": tipo_canal
            }

            resultados_finales.append(
                resultado
            )
            
        # Algunos recursos recuperados por la API pueden presentar
        # información incompleta o inconsistente. En esos casos se
        # omite únicamente el recurso afectado para continuar el
        # procesamiento del resto de los resultados.

        except Exception:
            # Continúa procesando los demás elementos para evitar que un
            # recurso con información incompleta interrumpa la recuperación.
            continue
    
    return resultados_finales
