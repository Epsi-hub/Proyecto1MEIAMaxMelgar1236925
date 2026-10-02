import csv
import os
import xml.etree.ElementTree as ET

from src.configuracion import ruta_registros, ruta_xml
from src.utilidades import validar_registro


CAMPOS = [
    "id",
    "nombre",
    "categoria",
    "descripcion",
    "fecha",
    "estado"
]


class ErrorFormatoCSV(Exception):
    """
    Se lanza cuando el archivo principal no tiene
    los encabezados o las columnas esperadas.
    """


def _crear_carpeta_de(ruta):

    carpeta = os.path.dirname(ruta)

    if carpeta:
        os.makedirs(carpeta, exist_ok=True)


def crear_archivo_si_no_existe():
    """
    Crea el archivo CSV con sus encabezados si:
    - no existe, o
    - existe pero está vacío (0 bytes).
    """

    ruta = ruta_registros()

    _crear_carpeta_de(ruta)

    if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:

        with open(
            ruta, "w", newline="", encoding="utf-8"
        ) as archivo:

            escritor = csv.DictWriter(
                archivo, fieldnames=CAMPOS
            )

            escritor.writeheader()


def leer_registros():
    """
    Lee todos los registros del CSV.

    Lanza ErrorFormatoCSV si los encabezados no coinciden
    o si alguna fila tiene columnas de más o de menos.
    """

    crear_archivo_si_no_existe()

    registros = []

    with open(
        ruta_registros(), "r", newline="", encoding="utf-8-sig"
    ) as archivo:

        lector = csv.DictReader(archivo)

        if lector.fieldnames != CAMPOS:
            raise ErrorFormatoCSV(
                "El archivo principal no tiene los encabezados "
                f"esperados: {','.join(CAMPOS)}"
            )

        for numero, fila in enumerate(lector, start=2):

            if None in fila or None in fila.values():
                raise ErrorFormatoCSV(
                    f"La línea {numero} del archivo principal "
                    "tiene un formato incorrecto."
                )

            registros.append(fila)

    return registros


def existe_id(id_registro):
    """
    Verifica si ya existe un registro con ese ID.
    """

    for registro in leer_registros():

        if registro["id"] == id_registro:
            return True

    return False


def agregar_registro(registro):
    """
    Agrega un registro al final del CSV.

    Retorna False si el ID ya existe.
    Lanza ValueError si algún campo no es válido.
    """

    errores = validar_registro(registro)

    if errores:
        raise ValueError(" ".join(errores))

    registro = {
        campo: registro[campo].strip() for campo in CAMPOS
    }

    if existe_id(registro["id"]):
        return False

    with open(
        ruta_registros(), "a", newline="", encoding="utf-8"
    ) as archivo:

        escritor = csv.DictWriter(
            archivo, fieldnames=CAMPOS
        )

        escritor.writerow(registro)

    return True


def buscar_registro_por_id(id_registro):
    """
    Busca un registro por ID recorriendo el archivo.
    """

    for registro in leer_registros():

        if registro["id"] == id_registro:
            return registro

    return None


def _reescribir(registros):
    """
    Reescribe el CSV completo de forma segura:
    primero escribe un archivo temporal y luego lo
    reemplaza, para no dejar el archivo a medias.
    """

    ruta = ruta_registros()
    temporal = ruta + ".tmp"

    with open(
        temporal, "w", newline="", encoding="utf-8"
    ) as archivo:

        escritor = csv.DictWriter(
            archivo, fieldnames=CAMPOS
        )

        escritor.writeheader()
        escritor.writerows(registros)

    os.replace(temporal, ruta)


def actualizar_registro(id_registro, nuevos_datos):
    """
    Actualiza un registro existente.
    Lanza ValueError si los nuevos datos no son válidos.
    """

    completo = dict(nuevos_datos)
    completo["id"] = id_registro

    errores = validar_registro(completo)

    if errores:
        raise ValueError(" ".join(errores))

    registros = leer_registros()

    encontrado = False

    for registro in registros:

        if registro["id"] == id_registro:

            for campo in CAMPOS:
                if campo != "id":
                    registro[campo] = nuevos_datos[campo].strip()

            encontrado = True
            break

    if not encontrado:
        return False

    _reescribir(registros)

    return True


def eliminar_registro(id_registro):
    """
    Elimina un registro del CSV.
    """

    registros = leer_registros()

    restantes = [
        r for r in registros if r["id"] != id_registro
    ]

    if len(restantes) == len(registros):
        return False

    _reescribir(restantes)

    return True


def exportar_a_xml():
    """
    Exporta todos los registros del CSV a XML.

    Estructura:
    <registros>
        <registro>
            <id>..</id> <nombre>..</nombre> ...
        </registro>
    </registros>
    """

    registros = leer_registros()

    ruta = ruta_xml()

    _crear_carpeta_de(ruta)

    raiz = ET.Element("registros")

    for registro in registros:

        elemento = ET.SubElement(raiz, "registro")

        for campo in CAMPOS:

            hijo = ET.SubElement(elemento, campo)
            hijo.text = registro[campo]

    arbol = ET.ElementTree(raiz)

    ET.indent(arbol, space="    ")

    arbol.write(
        ruta, encoding="utf-8", xml_declaration=True
    )

    return ruta