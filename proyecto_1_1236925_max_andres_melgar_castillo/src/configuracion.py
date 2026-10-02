import json
import os


RUTA_CONFIG = "config/configuracion.json"

VALORES_POR_DEFECTO = {
    "nombre_sistema": "Sistema Integral de Gestión y Recuperación de Información",
    "version": "1.0",
    "archivo_principal": "data/registros.csv",
    "formato_principal": "CSV",
    "archivo_exportacion": "exports/registros.xml",
    "carpeta_indices": "indices",
    "carpeta_logs": "logs",
    "carpeta_respaldos": "backups",
    "algoritmo_integridad": "SHA-256",
    "tamanio_tabla_hash": 10
}


def cargar_configuracion():
    """
    Lee config/configuracion.json y retorna un diccionario.

    - Si el archivo no existe, lo crea con los valores por defecto.
    - Si está dañado o incompleto, usa los valores por defecto
      para las claves que falten (el sistema no se detiene).
    """

    configuracion = dict(VALORES_POR_DEFECTO)

    if not os.path.exists(RUTA_CONFIG):

        try:
            os.makedirs("config", exist_ok=True)

            with open(
                RUTA_CONFIG, "w", encoding="utf-8"
            ) as archivo:
                json.dump(
                    VALORES_POR_DEFECTO,
                    archivo,
                    indent=4,
                    ensure_ascii=False
                )
        except OSError:
            pass

        return configuracion

    try:
        with open(
            RUTA_CONFIG, "r", encoding="utf-8"
        ) as archivo:
            leido = json.load(archivo)

        if isinstance(leido, dict):
            configuracion.update(leido)

    except (OSError, json.JSONDecodeError):
        pass

    return configuracion


def obtener(clave):
    """
    Retorna el valor de una clave de configuración.
    """

    return cargar_configuracion().get(
        clave,
        VALORES_POR_DEFECTO.get(clave)
    )


def _unir(carpeta, nombre):
    return f"{str(carpeta).rstrip('/')}/{nombre}"


def tamanio_tabla():
    """
    Tamaño de la tabla hash (debe ser un entero positivo).
    """

    valor = obtener("tamanio_tabla_hash")

    if (
        isinstance(valor, int)
        and not isinstance(valor, bool)
        and valor > 0
    ):
        return valor

    return VALORES_POR_DEFECTO["tamanio_tabla_hash"]


def ruta_registros():
    return obtener("archivo_principal")


def ruta_xml():
    return obtener("archivo_exportacion")


def carpeta_indices():
    return obtener("carpeta_indices")


def ruta_indice_id():
    return _unir(carpeta_indices(), "indice_id.json")


def ruta_indice_categoria():
    return _unir(carpeta_indices(), "indice_categoria.json")


def ruta_indice_estado():
    return _unir(carpeta_indices(), "indice_estado.json")


def ruta_tabla_hash():
    return _unir(carpeta_indices(), "tabla_hash.json")


def ruta_hashes():
    return _unir(carpeta_indices(), "hashes.json")


def ruta_log():
    return _unir(obtener("carpeta_logs"), "sistema.log")


def carpeta_respaldos():
    return obtener("carpeta_respaldos")