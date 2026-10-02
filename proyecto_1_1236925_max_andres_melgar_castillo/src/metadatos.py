import os
import stat
from datetime import datetime

from src.configuracion import (
    RUTA_CONFIG,
    ruta_registros,
    ruta_xml,
    ruta_indice_id,
    ruta_indice_categoria,
    ruta_indice_estado,
    ruta_tabla_hash,
    ruta_hashes,
    ruta_log
)


def obtener_metadatos(ruta_archivo):
    """
    Obtiene los metadatos principales de un archivo
    (None si el archivo no existe).
    """

    if not os.path.exists(ruta_archivo):
        return None

    informacion = os.stat(ruta_archivo)

    return {
        "nombre": os.path.basename(ruta_archivo),
        "ruta": os.path.abspath(ruta_archivo),
        "extension": os.path.splitext(ruta_archivo)[1],
        "tamanio": informacion.st_size,
        "fecha_creacion": datetime.fromtimestamp(
            informacion.st_ctime
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "fecha_modificacion": datetime.fromtimestamp(
            informacion.st_mtime
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "permisos": stat.filemode(informacion.st_mode)
    }


def listar_archivos_sistema():
    """
    Archivos reales utilizados por el sistema.
    """

    return [
        ruta_registros(),
        RUTA_CONFIG,
        ruta_indice_id(),
        ruta_indice_categoria(),
        ruta_indice_estado(),
        ruta_tabla_hash(),
        ruta_hashes(),
        ruta_xml(),
        ruta_log()
    ]