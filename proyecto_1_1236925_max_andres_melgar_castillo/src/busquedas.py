from src.archivos import leer_registros, CAMPOS


def busqueda_secuencial_por_id(id_buscado):
    """
    Recorre el archivo principal registro por registro
    hasta encontrar el ID.

    Retorna:
    - registro encontrado (o None)
    - cantidad de registros recorridos
    """

    recorridos = 0

    for registro in leer_registros():

        recorridos += 1

        if registro["id"] == id_buscado:
            return registro, recorridos

    return None, recorridos


def busqueda_por_atributo(atributo, valor):
    """
    Búsqueda secuencial de todos los registros cuyo
    atributo coincide con el valor (sin distinguir
    mayúsculas de minúsculas).
    """

    if atributo not in CAMPOS:
        raise ValueError(f"Atributo desconocido: {atributo}")

    valor = valor.strip().lower()

    return [
        registro
        for registro in leer_registros()
        if registro[atributo].strip().lower() == valor
    ]