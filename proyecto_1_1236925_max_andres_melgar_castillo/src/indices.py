import json
import os

from src.archivos import leer_registros
from src.configuracion import (
    carpeta_indices,
    ruta_indice_id,
    ruta_indice_categoria,
    ruta_indice_estado
)
from src.logs import registrar_log


def _guardar_json(ruta, datos):

    os.makedirs(carpeta_indices(), exist_ok=True)

    with open(ruta, "w", encoding="utf-8") as archivo:

        json.dump(
            datos, archivo, indent=4, ensure_ascii=False
        )


def _construir_indices(registros):
    """
    Construye en memoria los tres índices a partir
    de los registros del archivo principal.

    - indice_id:        ID -> posición del registro
    - indice_categoria: categoría -> [IDs]   (invertido)
    - indice_estado:    estado -> [IDs]      (invertido)
    """

    por_id = {}
    por_categoria = {}
    por_estado = {}

    for posicion, registro in enumerate(registros):

        por_id[registro["id"]] = posicion

        por_categoria.setdefault(
            registro["categoria"], []
        ).append(registro["id"])

        por_estado.setdefault(
            registro["estado"], []
        ).append(registro["id"])

    return por_id, por_categoria, por_estado


def generar_indice_id():

    indice = _construir_indices(leer_registros())[0]
    _guardar_json(ruta_indice_id(), indice)
    return indice


def generar_indice_categoria():

    indice = _construir_indices(leer_registros())[1]
    _guardar_json(ruta_indice_categoria(), indice)
    return indice


def generar_indice_estado():

    indice = _construir_indices(leer_registros())[2]
    _guardar_json(ruta_indice_estado(), indice)
    return indice


def generar_todos_los_indices(
    operacion="INDEX_GENERATE",
    motivo="Generación de índices"
):
    """
    Reconstruye los tres índices leyendo el archivo
    principal una sola vez y deja constancia en el log.
    """

    por_id, por_categoria, por_estado = _construir_indices(
        leer_registros()
    )

    _guardar_json(ruta_indice_id(), por_id)
    _guardar_json(ruta_indice_categoria(), por_categoria)
    _guardar_json(ruta_indice_estado(), por_estado)

    registrar_log(operacion, motivo)


def cargar_indice(ruta):
    """
    Carga un índice desde disco.
    Retorna None si el archivo no existe o está dañado.
    """

    if not os.path.exists(ruta):
        return None

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except (OSError, json.JSONDecodeError):
        return None


def indices_estan_actualizados():
    """
    Compara los índices guardados contra lo que debería
    contener el archivo principal. Detecta:
    - índice inexistente
    - índice dañado
    - índice desactualizado
    """

    esperados = _construir_indices(leer_registros())

    rutas = [
        ruta_indice_id(),
        ruta_indice_categoria(),
        ruta_indice_estado()
    ]

    for ruta, esperado in zip(rutas, esperados):

        if cargar_indice(ruta) != esperado:
            return False

    return True


def asegurar_indices():
    """
    Si algún índice no existe, está dañado o no coincide
    con el archivo principal, lo reconstruye.

    Retorna True si fue necesario reconstruir.
    """

    if indices_estan_actualizados():
        return False

    generar_todos_los_indices(
        operacion="INDEX_AUTO",
        motivo=(
            "Índice inexistente o desactualizado; "
            "reconstruido automáticamente"
        )
    )

    return True


def buscar_por_indice_id(id_buscado):
    """
    Búsqueda con el índice principal (ID -> posición).

    Retorna (registro, posición) o (None, None).
    """

    indice = cargar_indice(ruta_indice_id()) or {}

    if id_buscado not in indice:
        return None, None

    posicion = indice[id_buscado]

    registros = leer_registros()

    if posicion >= len(registros):
        return None, None

    registro = registros[posicion]

    if registro["id"] != id_buscado:
        return None, None

    return registro, posicion


def _buscar_por_indice_invertido(ruta, valor):
    """
    Consulta un índice invertido (valor -> [IDs]) y
    recupera cada registro mediante el índice principal.
    """

    invertido = cargar_indice(ruta) or {}
    principal = cargar_indice(ruta_indice_id()) or {}

    ids = []

    for clave, lista in invertido.items():

        if clave.strip().lower() == valor.strip().lower():
            ids = lista
            break

    registros = leer_registros()

    resultados = []

    for id_registro in ids:

        posicion = principal.get(id_registro)

        if posicion is not None and posicion < len(registros):
            resultados.append(registros[posicion])

    return resultados


def buscar_por_indice_categoria(categoria):

    return _buscar_por_indice_invertido(
        ruta_indice_categoria(), categoria
    )


def buscar_por_indice_estado(estado):

    return _buscar_por_indice_invertido(
        ruta_indice_estado(), estado
    )