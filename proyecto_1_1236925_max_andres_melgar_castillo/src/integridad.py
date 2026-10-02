import hashlib
import json
import os

from src.configuracion import (
    RUTA_CONFIG,
    carpeta_indices,
    ruta_registros,
    ruta_indice_id,
    ruta_indice_categoria,
    ruta_indice_estado,
    ruta_hashes
)


def archivos_protegidos():
    """
    Archivos cuya huella SHA-256 se registra y verifica.
    """

    return [
        ruta_registros(),
        RUTA_CONFIG,
        ruta_indice_id(),
        ruta_indice_categoria(),
        ruta_indice_estado()
    ]


def calcular_sha256(ruta_archivo):
    """
    Calcula el SHA-256 de un archivo leyéndolo por bloques.
    """

    sha256 = hashlib.sha256()

    with open(ruta_archivo, "rb") as archivo:

        while True:

            bloque = archivo.read(4096)

            if not bloque:
                break

            sha256.update(bloque)

    return sha256.hexdigest()


def guardar_hashes():
    """
    Calcula y guarda los hashes actuales de los
    archivos protegidos en indices/hashes.json.
    """

    os.makedirs(carpeta_indices(), exist_ok=True)

    hashes = {}

    for ruta in archivos_protegidos():

        if os.path.exists(ruta):
            hashes[ruta] = calcular_sha256(ruta)

    with open(ruta_hashes(), "w", encoding="utf-8") as archivo:

        json.dump(
            hashes, archivo, indent=4, ensure_ascii=False
        )

    return hashes


def cargar_hashes():
    """
    Recupera los hashes registrados (diccionario vacío si
    el archivo no existe o está dañado).
    """

    if not os.path.exists(ruta_hashes()):
        return {}

    try:
        with open(
            ruta_hashes(), "r", encoding="utf-8"
        ) as archivo:

            datos = json.load(archivo)

            return datos if isinstance(datos, dict) else {}

    except (OSError, json.JSONDecodeError):
        return {}


def verificar_integridad():
    """
    Compara el hash registrado contra el hash actual de
    cada archivo protegido.

    Estados: OK, ALTERADO, SIN HASH REGISTRADO, NO EXISTE.
    """

    guardados = cargar_hashes()

    resultados = []

    for ruta in archivos_protegidos():

        hash_guardado = guardados.get(ruta)

        if not os.path.exists(ruta):

            resultados.append({
                "archivo": ruta,
                "estado": "NO EXISTE",
                "hash_guardado": hash_guardado,
                "hash_actual": None
            })

            continue

        hash_actual = calcular_sha256(ruta)

        if hash_guardado is None:
            estado = "SIN HASH REGISTRADO"

        elif hash_actual == hash_guardado:
            estado = "OK"

        else:
            estado = "ALTERADO"

        resultados.append({
            "archivo": ruta,
            "estado": estado,
            "hash_guardado": hash_guardado,
            "hash_actual": hash_actual
        })

    return resultados