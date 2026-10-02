import os
from datetime import datetime

from src.configuracion import ruta_log


ENCABEZADO = "=== LOG DEL SISTEMA ==="


def preparar_log():
    """
    Crea la carpeta y el archivo de log si no existen
    o si el archivo está vacío.
    """

    ruta = ruta_log()

    carpeta = os.path.dirname(ruta)

    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:

        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(ENCABEZADO + "\n")


def registrar_log(operacion, descripcion):
    """
    Agrega una línea al log con el formato:
    fecha | hora | operación | descripción
    """

    preparar_log()

    ahora = datetime.now()

    descripcion = " ".join(str(descripcion).split())

    linea = (
        f"{ahora.strftime('%Y-%m-%d')} | "
        f"{ahora.strftime('%H:%M:%S')} | "
        f"{operacion} | "
        f"{descripcion}\n"
    )

    with open(ruta_log(), "a", encoding="utf-8") as archivo:
        archivo.write(linea)


def leer_logs():
    """
    Retorna las líneas de operaciones registradas
    (sin la línea de encabezado).
    """

    preparar_log()

    with open(ruta_log(), "r", encoding="utf-8") as archivo:

        return [
            linea
            for linea in archivo.readlines()
            if not linea.startswith("===")
        ]