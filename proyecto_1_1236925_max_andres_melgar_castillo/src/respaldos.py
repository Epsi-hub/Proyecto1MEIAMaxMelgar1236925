import csv
import os
import shutil
from datetime import datetime

from src.archivos import CAMPOS
from src.configuracion import (
    RUTA_CONFIG,
    carpeta_respaldos,
    ruta_registros,
    ruta_xml,
    ruta_hashes
)


def _archivos_respaldo():
    """
    Archivos que forman parte de un respaldo:
    nombre dentro del respaldo -> ubicación original.

    Se respaldan los datos principales, la configuración,
    la exportación XML y los hashes de integridad.
    Los índices y la tabla hash NO se respaldan porque son
    estructuras derivadas: se reconstruyen desde el CSV.
    """

    rutas = [
        ruta_registros(),
        RUTA_CONFIG,
        ruta_xml(),
        ruta_hashes()
    ]

    return {os.path.basename(ruta): ruta for ruta in rutas}


def crear_respaldo():
    """
    Crea una carpeta backup_AAAAMMDD_HHMMSS (nombre generado
    con la fecha y hora del sistema) y copia los archivos.

    Retorna (nombre, ruta, archivos_copiados).
    """

    carpeta = carpeta_respaldos()

    os.makedirs(carpeta, exist_ok=True)

    nombre = "backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    ruta_backup = os.path.join(carpeta, nombre)

    os.makedirs(ruta_backup, exist_ok=True)

    copiados = []

    for nombre_archivo, ruta_original in _archivos_respaldo().items():

        if os.path.exists(ruta_original):

            shutil.copy2(
                ruta_original,
                os.path.join(ruta_backup, nombre_archivo)
            )

            copiados.append(nombre_archivo)

    if not copiados:
        shutil.rmtree(ruta_backup, ignore_errors=True)

    return nombre, ruta_backup, copiados


def listar_respaldos():
    """
    Respaldos disponibles, del más reciente al más antiguo.
    """

    carpeta = carpeta_respaldos()

    os.makedirs(carpeta, exist_ok=True)

    respaldos = [
        elemento
        for elemento in os.listdir(carpeta)
        if elemento.startswith("backup_")
        and os.path.isdir(os.path.join(carpeta, elemento))
    ]

    respaldos.sort(reverse=True)

    return respaldos


def _csv_valido(ruta):
    """
    Verifica que un CSV tenga los encabezados esperados
    y que todas sus filas tengan el número de columnas correcto.
    """

    try:
        with open(
            ruta, "r", newline="", encoding="utf-8-sig"
        ) as archivo:

            lector = csv.DictReader(archivo)

            if lector.fieldnames != CAMPOS:
                return False

            for fila in lector:
                if None in fila or None in fila.values():
                    return False

        return True

    except (OSError, csv.Error, UnicodeDecodeError):
        return False


def restaurar_respaldo(nombre_backup):
    """
    Restaura los archivos de un respaldo.

    Antes de tocar el sistema actual valida que el respaldo
    exista y que su archivo principal sea correcto. Si ocurre
    un error a mitad de la copia, devuelve los archivos a su
    estado anterior.

    Retorna (exito, archivos_restaurados, mensaje).
    """

    ruta_backup = os.path.join(carpeta_respaldos(), nombre_backup)

    if not os.path.isdir(ruta_backup):
        return False, [], "El respaldo seleccionado no existe."

    archivos = _archivos_respaldo()

    nombre_csv = os.path.basename(ruta_registros())

    origen_csv = os.path.join(ruta_backup, nombre_csv)

    if not os.path.exists(origen_csv):
        return False, [], (
            "El respaldo no contiene el archivo principal."
        )

    if not _csv_valido(origen_csv):
        return False, [], (
            "El archivo principal del respaldo tiene un "
            "formato incorrecto."
        )

    estado_anterior = {}
    restaurados = []

    try:

        for nombre_archivo, destino in archivos.items():

            origen = os.path.join(ruta_backup, nombre_archivo)

            if not os.path.exists(origen):
                continue

            if os.path.exists(destino):
                with open(destino, "rb") as actual:
                    estado_anterior[destino] = actual.read()
            else:
                estado_anterior[destino] = None

            carpeta_destino = os.path.dirname(destino)

            if carpeta_destino:
                os.makedirs(carpeta_destino, exist_ok=True)

            shutil.copy2(origen, destino)

            restaurados.append(destino)

    except Exception as error:

        for destino, contenido in estado_anterior.items():

            try:
                if contenido is None:
                    if os.path.exists(destino):
                        os.remove(destino)
                else:
                    with open(destino, "wb") as actual:
                        actual.write(contenido)
            except OSError:
                pass

        return False, [], (
            f"Error durante la restauración ({error}). "
            "Se conservó el estado anterior."
        )

    return True, restaurados, "Respaldo restaurado correctamente."