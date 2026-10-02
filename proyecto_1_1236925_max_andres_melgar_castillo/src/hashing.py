import json
import os

from src.archivos import leer_registros
from src.configuracion import (
    carpeta_indices,
    ruta_tabla_hash,
    tamanio_tabla
)
from src.logs import registrar_log


def funcion_hash(id_registro):
    """
    Función hash por división.

    posición = ID % tamaño_de_la_tabla

    Ejemplo (tamaño 10):  1001 % 10 = 1
    El tamaño se lee de config/configuracion.json.
    Lanza ValueError si el ID no es numérico.
    """

    texto = str(id_registro).strip()

    if not (texto.isascii() and texto.isdigit()):
        raise ValueError("El ID debe ser numérico.")

    return int(texto) % tamanio_tabla()


def _construir_tabla():
    """
    Tabla hash con encadenamiento: cada posición guarda
    una lista con los IDs que caen en ella.
    """

    tabla = {str(p): [] for p in range(tamanio_tabla())}

    for registro in leer_registros():

        try:
            posicion = funcion_hash(registro["id"])
        except ValueError:
            continue

        tabla[str(posicion)].append(registro["id"])

    return tabla


def generar_tabla_hash():
    """
    Genera la tabla hash desde el CSV y la guarda en disco.
    """

    os.makedirs(carpeta_indices(), exist_ok=True)

    tabla = _construir_tabla()

    with open(
        ruta_tabla_hash(), "w", encoding="utf-8"
    ) as archivo:

        json.dump(
            tabla, archivo, indent=4, ensure_ascii=False
        )

    return tabla


def _leer_tabla_guardada():

    if not os.path.exists(ruta_tabla_hash()):
        return None

    try:
        with open(
            ruta_tabla_hash(), "r", encoding="utf-8"
        ) as archivo:
            return json.load(archivo)

    except (OSError, json.JSONDecodeError):
        return None


def cargar_tabla_hash():
    """
    Carga la tabla hash guardada. Si no existe, está dañada,
    tiene otro tamaño o no coincide con el CSV, la regenera.
    """

    esperada = _construir_tabla()

    if _leer_tabla_guardada() != esperada:

        tabla = generar_tabla_hash()

        registrar_log(
            "HASH_AUTO",
            "Tabla hash inexistente o desactualizada; "
            "regenerada automáticamente"
        )

        return tabla

    return esperada


def buscar_por_hash(id_buscado):
    """
    Busca un ID usando la tabla hash.

    1. Calcula la posición con la función hash.
    2. Revisa solo la cadena de esa posición.
    3. Si el ID está, recupera el registro del CSV.

    Retorna (registro, posición, cadena_revisada).
    """

    id_buscado = id_buscado.strip()

    posicion = funcion_hash(id_buscado)

    tabla = cargar_tabla_hash()

    cadena = tabla.get(str(posicion), [])

    if id_buscado not in cadena:
        return None, posicion, cadena

    for registro in leer_registros():

        if registro["id"] == id_buscado:
            return registro, posicion, cadena

    return None, posicion, cadena


def obtener_colisiones():
    """
    Posiciones que contienen más de un ID.
    """

    tabla = cargar_tabla_hash()

    return {
        posicion: ids
        for posicion, ids in tabla.items()
        if len(ids) > 1
    }