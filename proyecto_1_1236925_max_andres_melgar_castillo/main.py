from src.archivos import (
    ErrorFormatoCSV,
    crear_archivo_si_no_existe,
    leer_registros,
    existe_id,
    agregar_registro,
    buscar_registro_por_id,
    actualizar_registro,
    eliminar_registro,
    exportar_a_xml
)

from src.busquedas import (
    busqueda_secuencial_por_id,
    busqueda_por_atributo
)

from src.configuracion import (
    cargar_configuracion,
    ruta_indice_id,
    ruta_indice_categoria,
    ruta_indice_estado,
    tamanio_tabla
)

from src.indices import (
    generar_todos_los_indices,
    asegurar_indices,
    cargar_indice,
    buscar_por_indice_id,
    buscar_por_indice_categoria,
    buscar_por_indice_estado
)

from src.hashing import (
    generar_tabla_hash,
    cargar_tabla_hash,
    buscar_por_hash,
    obtener_colisiones,
    funcion_hash
)

from src.integridad import (
    guardar_hashes,
    cargar_hashes,
    verificar_integridad
)

from src.logs import (
    preparar_log,
    registrar_log,
    leer_logs
)

from src.metadatos import (
    obtener_metadatos,
    listar_archivos_sistema
)

from src.respaldos import (
    crear_respaldo,
    listar_respaldos,
    restaurar_respaldo
)

from src.pila import PilaOperaciones

from src.utilidades import (
    validar_id,
    validar_fecha,
    validar_texto
)


pila_operaciones = PilaOperaciones()


# Campos que se piden al registrar / actualizar:
# (campo, etiqueta, validador)
CAMPOS_FORMULARIO = [
    ("nombre", "Nombre", lambda v: validar_texto(v, "El nombre")),
    ("categoria", "Categoría", lambda v: validar_texto(v, "La categoría")),
    ("descripcion", "Descripción", lambda v: validar_texto(v, "La descripción")),
    ("fecha", "Fecha (AAAA-MM-DD)", validar_fecha),
    ("estado", "Estado", lambda v: validar_texto(v, "El estado"))
]


# ---------------------------------------------------------------
# Utilidades de interfaz
# ---------------------------------------------------------------

def mostrar_registro(registro):
    print("\n-----------------------------")
    print(f"ID:          {registro['id']}")
    print(f"Nombre:      {registro['nombre']}")
    print(f"Categoría:   {registro['categoria']}")
    print(f"Descripción: {registro['descripcion']}")
    print(f"Fecha:       {registro['fecha']}")
    print(f"Estado:      {registro['estado']}")
    print("-----------------------------")


def pedir(mensaje, validador=None):
    """
    Pide un dato hasta que sea válido.
    Retorna None si el usuario escribe 'cancelar'.
    """

    while True:

        valor = input(mensaje).strip()

        if valor.lower() == "cancelar":
            return None

        if validador is not None:

            error = validador(valor)

            if error:
                print(f"  ✗ {error} (escriba 'cancelar' para volver)")
                continue

        return valor


def operacion_cancelada():
    print("\nOperación cancelada.")


def actualizar_estructuras(motivo):
    """
    Mantiene consistentes las estructuras derivadas del
    archivo principal después de crear, modificar o eliminar.
    """

    generar_todos_los_indices(motivo=f"Índices generados ({motivo})")
    generar_tabla_hash()
    registrar_log("HASH_TABLE", f"Tabla hash regenerada ({motivo})")
    guardar_hashes()
    registrar_log(
        "INTEGRITY_REGISTER",
        f"Hashes SHA-256 actualizados ({motivo})"
    )

    print("Índices actualizados correctamente.")
    print("Tabla hash actualizada correctamente.")
    print("Hashes de integridad actualizados.")


def avisar_si_se_reconstruyeron_indices():

    if asegurar_indices():
        print(
            "\nAviso: un índice no existía o estaba desactualizado, "
            "por lo que fue reconstruido automáticamente."
        )


# ---------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------

def registrar_informacion():

    print("\n=== REGISTRAR INFORMACIÓN ===")
    print("(Escriba 'cancelar' en cualquier campo para volver)")

    id_registro = pedir("ID (numérico): ", validar_id)

    if id_registro is None:
        return operacion_cancelada()

    if existe_id(id_registro):

        registrar_log(
            "CREATE_ERROR",
            f"Intento de registrar ID duplicado {id_registro}"
        )

        print("\nERROR: El ID ingresado ya existe.")
        return

    registro = {"id": id_registro}

    for campo, etiqueta, validador in CAMPOS_FORMULARIO:

        valor = pedir(f"{etiqueta}: ", validador)

        if valor is None:
            return operacion_cancelada()

        registro[campo] = valor

    agregar_registro(registro)

    registrar_log("CREATE", f"Registro creado con ID {id_registro}")

    pila_operaciones.push(f"CREATE - Registro {id_registro}")

    print("\nRegistro almacenado correctamente.")

    actualizar_estructuras(f"alta del registro {id_registro}")


def mostrar_todos():

    print("\n=== REGISTROS ALMACENADOS ===")

    registros = leer_registros()

    registrar_log(
        "QUERY",
        f"Consulta de todos los registros ({len(registros)})"
    )

    if not registros:
        print("No existen registros.")
        return

    for registro in registros:
        mostrar_registro(registro)

    print(f"\nTotal de registros: {len(registros)}")


def buscar_por_id():

    print("\n=== BÚSQUEDA SECUENCIAL POR ID ===")

    id_registro = pedir("Ingrese el ID: ")

    if not id_registro:
        return operacion_cancelada()

    registro, recorridos = busqueda_secuencial_por_id(id_registro)

    print(f"\nValor buscado: ID = {id_registro}")

    if registro is None:

        print("Resultado: NO ENCONTRADO")

        registrar_log(
            "SEARCH",
            f"Búsqueda secuencial sin resultado para ID {id_registro} "
            f"({recorridos} registros recorridos)"
        )

    else:

        mostrar_registro(registro)
        print("Resultado: ENCONTRADO")

        registrar_log(
            "SEARCH",
            f"Búsqueda secuencial exitosa para ID {id_registro} "
            f"({recorridos} registros recorridos)"
        )

        pila_operaciones.push(f"SEARCH - Registro {id_registro}")

    print(f"Registros recorridos: {recorridos}")


def actualizar():

    print("\n=== ACTUALIZAR REGISTRO ===")

    id_registro = pedir("Ingrese el ID: ")

    if not id_registro:
        return operacion_cancelada()

    registro = buscar_registro_por_id(id_registro)

    if registro is None:

        registrar_log(
            "UPDATE_ERROR",
            f"ID inexistente al actualizar: {id_registro}"
        )

        print("\nRegistro no encontrado.")
        return

    print("\nInformación actual:")
    mostrar_registro(registro)

    print(
        "\nIngrese la nueva información "
        "(Enter = conservar el valor actual, "
        "'cancelar' = volver):"
    )

    nuevos_datos = {}

    for campo, etiqueta, validador in CAMPOS_FORMULARIO:

        while True:

            valor = input(f"{etiqueta} [{registro[campo]}]: ").strip()

            if valor.lower() == "cancelar":
                return operacion_cancelada()

            if valor == "":
                nuevos_datos[campo] = registro[campo]
                break

            error = validador(valor)

            if error:
                print(f"  ✗ {error}")
                continue

            nuevos_datos[campo] = valor
            break

    if actualizar_registro(id_registro, nuevos_datos):

        registrar_log(
            "UPDATE",
            f"Registro actualizado con ID {id_registro}"
        )

        pila_operaciones.push(f"UPDATE - Registro {id_registro}")

        print("\nRegistro actualizado correctamente.")

        actualizar_estructuras(f"modificación del registro {id_registro}")

    else:

        registrar_log(
            "UPDATE_ERROR",
            f"No fue posible actualizar ID {id_registro}"
        )

        print("\nNo fue posible actualizar el registro.")


def eliminar():

    print("\n=== ELIMINAR REGISTRO ===")

    id_registro = pedir("Ingrese el ID: ")

    if not id_registro:
        return operacion_cancelada()

    registro = buscar_registro_por_id(id_registro)

    if registro is None:

        registrar_log(
            "DELETE_ERROR",
            f"ID inexistente al eliminar: {id_registro}"
        )

        print("\nRegistro no encontrado.")
        return

    mostrar_registro(registro)

    confirmacion = input(
        "\n¿Está seguro de eliminar este registro? (s/n): "
    ).strip().lower()

    if confirmacion != "s":

        registrar_log(
            "DELETE_CANCEL",
            f"Eliminación cancelada para ID {id_registro}"
        )

        print("\nOperación cancelada.")
        return

    if eliminar_registro(id_registro):

        registrar_log(
            "DELETE",
            f"Registro eliminado con ID {id_registro}"
        )

        pila_operaciones.push(f"DELETE - Registro {id_registro}")

        print("\nRegistro eliminado correctamente.")

        actualizar_estructuras(f"baja del registro {id_registro}")


# ---------------------------------------------------------------
# Búsquedas
# ---------------------------------------------------------------

def buscar_por_atributo():

    print("\n=== BUSCAR POR ATRIBUTO (secuencial) ===")

    print("1. Nombre")
    print("2. Categoría")
    print("3. Estado")
    print("4. Fecha")

    atributos = {
        "1": "nombre",
        "2": "categoria",
        "3": "estado",
        "4": "fecha"
    }

    opcion = input("Seleccione el atributo: ").strip()

    if opcion not in atributos:
        print("\nOpción inválida.")
        return

    atributo = atributos[opcion]

    valor = pedir(f"Ingrese {atributo}: ")

    if not valor:
        return operacion_cancelada()

    resultados = busqueda_por_atributo(atributo, valor)

    registrar_log(
        "SEARCH_ATTRIBUTE",
        f"Búsqueda por {atributo} = '{valor}': "
        f"{len(resultados)} resultado(s)"
    )

    if not resultados:
        print("\nNo se encontraron registros.")
        return

    print(f"\nSe encontraron {len(resultados)} registro(s):")

    for registro in resultados:
        mostrar_registro(registro)


# ---------------------------------------------------------------
# Índices
# ---------------------------------------------------------------

def mostrar_indice_principal():

    print("\n=== ÍNDICE PRINCIPAL (ID -> posición) ===")

    avisar_si_se_reconstruyeron_indices()

    indice = cargar_indice(ruta_indice_id())

    registrar_log("QUERY", "Consulta del índice principal")

    if not indice:
        print("El índice está vacío (no hay registros).")
        return

    for id_registro, posicion in indice.items():
        print(f"ID: {id_registro} -> Posición: {posicion}")


def mostrar_indice_invertido():

    print("\n=== ÍNDICES INVERTIDOS ===")

    avisar_si_se_reconstruyeron_indices()

    registrar_log("QUERY", "Consulta de los índices invertidos")

    for titulo, ruta in [
        ("POR CATEGORÍA (categoría -> IDs)", ruta_indice_categoria()),
        ("POR ESTADO (estado -> IDs)", ruta_indice_estado())
    ]:

        print(f"\n{titulo}")

        indice = cargar_indice(ruta)

        if not indice:
            print("  (vacío)")
            continue

        for clave, ids in indice.items():
            print(f"  {clave} -> {ids}")


def buscar_utilizando_indice():

    print("\n=== BÚSQUEDA UTILIZANDO ÍNDICES ===")

    print("1. ID (índice principal)")
    print("2. Categoría (índice invertido)")
    print("3. Estado (índice invertido)")

    opcion = input("Seleccione el tipo de búsqueda: ").strip()

    if opcion not in ("1", "2", "3"):
        print("\nOpción inválida.")
        return

    avisar_si_se_reconstruyeron_indices()

    if opcion == "1":

        id_registro = pedir("Ingrese el ID: ")

        if not id_registro:
            return operacion_cancelada()

        registro, posicion = buscar_por_indice_id(id_registro)

        print(f"\nValor buscado: ID = {id_registro}")

        if registro is None:
            print("Resultado: NO ENCONTRADO")

        else:
            print(f"Posición obtenida del índice: {posicion}")
            mostrar_registro(registro)
            print("Resultado: ENCONTRADO")

            pila_operaciones.push(
                f"SEARCH_INDEX - Registro {id_registro}"
            )

        registrar_log(
            "SEARCH_INDEX",
            f"Búsqueda por índice de ID {id_registro}: "
            f"{'encontrado' if registro else 'sin resultado'}"
        )

        return

    if opcion == "2":
        etiqueta = "categoría"
        valor = pedir("Ingrese la categoría: ")
        funcion = buscar_por_indice_categoria
    else:
        etiqueta = "estado"
        valor = pedir("Ingrese el estado: ")
        funcion = buscar_por_indice_estado

    if not valor:
        return operacion_cancelada()

    resultados = funcion(valor)

    registrar_log(
        "SEARCH_INDEX",
        f"Búsqueda por índice invertido de {etiqueta} = '{valor}': "
        f"{len(resultados)} resultado(s)"
    )

    if not resultados:
        print("\nNo se encontraron registros.")
        return

    print(f"\nSe encontraron {len(resultados)} registro(s):")

    for registro in resultados:
        print(f"{registro['id']} - {registro['nombre']}")


def reconstruir_indices():

    print("\n=== RECONSTRUIR ÍNDICES ===")

    generar_todos_los_indices(
        operacion="INDEX_REBUILD",
        motivo="Reconstrucción manual de todos los índices"
    )

    print("\nTodos los índices fueron reconstruidos correctamente.")


# ---------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------

def mostrar_tabla_hash():

    print("\n=== TABLA HASH ===")
    print(f"Función hash: ID % {tamanio_tabla()}")
    print("Colisiones: encadenamiento (lista de IDs por posición)\n")

    tabla = cargar_tabla_hash()

    registrar_log("QUERY", "Consulta de la tabla hash")

    for posicion, ids in tabla.items():

        contenido = " -> ".join(ids) if ids else "VACÍO"

        print(f"Posición {posicion}: {contenido}")


def buscar_utilizando_hash():

    print("\n=== BÚSQUEDA MEDIANTE HASHING ===")

    id_registro = pedir("Ingrese el ID: ", validar_id)

    if id_registro is None:
        return operacion_cancelada()

    registro, posicion, cadena = buscar_por_hash(id_registro)

    print(
        f"\nPosición calculada: {id_registro} % {tamanio_tabla()} "
        f"= {posicion}"
    )

    print(f"IDs almacenados en esa posición: {cadena}")

    if registro is None:
        print("Resultado: NO ENCONTRADO")

    else:
        mostrar_registro(registro)
        print("Resultado: ENCONTRADO")

    registrar_log(
        "SEARCH_HASH",
        f"Búsqueda por hash del ID {id_registro} (posición {posicion}): "
        f"{'encontrado' if registro else 'sin resultado'}"
    )


def mostrar_colisiones():

    print("\n=== COLISIONES ===")

    colisiones = obtener_colisiones()

    registrar_log("QUERY", "Consulta de colisiones de la tabla hash")

    if not colisiones:
        print("Actualmente no existen colisiones.")
        return

    for posicion, ids in colisiones.items():
        print(f"Posición {posicion}: {ids}")


# ---------------------------------------------------------------
# Integridad
# ---------------------------------------------------------------

def registrar_integridad():

    print("\n=== REGISTRAR INTEGRIDAD ===")

    hashes = guardar_hashes()

    registrar_log(
        "INTEGRITY_REGISTER",
        "Hashes SHA-256 registrados manualmente"
    )

    if not hashes:
        print("\nNo existen archivos para registrar.")
        return

    print("\nHashes SHA-256 registrados:")

    for archivo, hash_archivo in hashes.items():
        print(f"\nArchivo: {archivo}")
        print(f"SHA-256: {hash_archivo}")


def imprimir_resultados_integridad(resultados):

    for resultado in resultados:

        registrar_log(
            "INTEGRITY_CHECK",
            f"{resultado['archivo']} -> {resultado['estado']}"
        )

        print("\n--------------------------------")
        print(f"Archivo: {resultado['archivo']}")
        print(f"Estado: {resultado['estado']}")
        print(f"Hash registrado: {resultado['hash_guardado']}")
        print(f"Hash actual: {resultado['hash_actual']}")

    print("\n--------------------------------")


def consultar_integridad():

    print("\n=== VERIFICACIÓN DE INTEGRIDAD ===")

    imprimir_resultados_integridad(verificar_integridad())


# ---------------------------------------------------------------
# Logs, pila y metadatos
# ---------------------------------------------------------------

def consultar_logs():

    print("\n=== LOG DEL SISTEMA ===")

    lineas = leer_logs()

    if not lineas:
        print("\nNo existen operaciones registradas.")
        return

    for linea in lineas:
        print(linea, end="")


def mostrar_pila():

    print("\n=== PILA DE OPERACIONES ===")

    if pila_operaciones.esta_vacia():
        print("\nLa pila está vacía.")
        return

    print("\nTOP")
    print(" │")
    print(" ▼")

    for operacion in pila_operaciones.obtener_elementos():
        print(f"[ {operacion} ]")

    print("\nCantidad de operaciones:", pila_operaciones.tamanio())


def consultar_top():

    print("\n=== TOP DE LA PILA ===")

    operacion = pila_operaciones.peek()

    if operacion is None:
        print("\nLa pila está vacía.")
    else:
        print(f"\nÚltima operación: {operacion}")


def retirar_operacion_pila():

    print("\n=== POP DE LA PILA ===")

    operacion = pila_operaciones.pop()

    if operacion is None:
        print("\nLa pila está vacía.")
        return

    print(f"\nOperación retirada: {operacion}")

    registrar_log(
        "STACK_POP",
        f"Operación retirada de la pila: {operacion}"
    )


def consultar_metadatos():

    print("\n=== METADATOS DE ARCHIVOS ===")

    existentes = [
        archivo
        for archivo in listar_archivos_sistema()
        if obtener_metadatos(archivo) is not None
    ]

    if not existentes:
        print("\nNo existen archivos disponibles.")
        return

    print()

    for posicion, archivo in enumerate(existentes, start=1):
        print(f"{posicion}. {archivo}")

    try:
        opcion = int(input("\nSeleccione un archivo: "))
    except ValueError:
        print("\nDebe ingresar un número.")
        return

    if opcion < 1 or opcion > len(existentes):
        print("\nOpción inválida.")
        return

    seleccionado = existentes[opcion - 1]

    metadatos = obtener_metadatos(seleccionado)

    if metadatos is None:
        print("\nEl archivo ya no existe.")
        return

    print("\n=== INFORMACIÓN DEL ARCHIVO ===")
    print(f"Nombre: {metadatos['nombre']}")
    print(f"Ruta: {metadatos['ruta']}")
    print(f"Extensión: {metadatos['extension']}")
    print(f"Tamaño: {metadatos['tamanio']} bytes")
    print(f"Fecha de creación: {metadatos['fecha_creacion']}")
    print(f"Última modificación: {metadatos['fecha_modificacion']}")
    print(f"Permisos: {metadatos['permisos']}")

    registrar_log("METADATA", f"Consulta de metadatos de {seleccionado}")

    pila_operaciones.push(f"METADATA - {seleccionado}")


# ---------------------------------------------------------------
# Exportación y respaldos
# ---------------------------------------------------------------

def exportar_informacion_xml():

    print("\n=== EXPORTAR INFORMACIÓN A XML ===")

    if not leer_registros():

        print("\nNo existen registros para exportar.")

        registrar_log(
            "EXPORT_ERROR",
            "Intento de exportar XML sin registros"
        )

        return

    ruta = exportar_a_xml()

    registrar_log("EXPORT_XML", f"Información exportada a {ruta}")

    pila_operaciones.push("EXPORT_XML - registros.xml")

    print("\nInformación exportada correctamente.")
    print(f"Archivo generado: {ruta}")


def generar_respaldo():

    print("\n=== GENERAR RESPALDO ===")

    nombre, ruta, archivos = crear_respaldo()

    if not archivos:

        print("\nNo existen archivos para respaldar.")

        registrar_log(
            "BACKUP_ERROR",
            "No existían archivos para respaldar"
        )

        return

    registrar_log("BACKUP", f"Respaldo generado: {nombre}")

    pila_operaciones.push(f"BACKUP - {nombre}")

    print("\nRespaldo generado correctamente.")
    print(f"Nombre: {nombre}")
    print(f"Ruta: {ruta}")

    print("\nArchivos respaldados:")

    for archivo in archivos:
        print(f"- {archivo}")


def consultar_respaldos():

    print("\n=== RESPALDOS DISPONIBLES ===")

    respaldos = listar_respaldos()

    if not respaldos:
        print("\nNo existen respaldos disponibles.")
        return

    for posicion, respaldo in enumerate(respaldos, start=1):
        print(f"{posicion}. {respaldo}")


def restaurar_desde_respaldo():

    print("\n=== RESTAURAR RESPALDO ===")

    respaldos = listar_respaldos()

    if not respaldos:
        print("\nNo existen respaldos disponibles.")
        return

    print("\nRespaldos disponibles:\n")

    for posicion, respaldo in enumerate(respaldos, start=1):
        print(f"{posicion}. {respaldo}")

    try:
        opcion = int(input("\nSeleccione el respaldo: "))
    except ValueError:
        print("\nDebe ingresar un número.")
        return

    if opcion < 1 or opcion > len(respaldos):
        print("\nOpción inválida.")
        return

    seleccionado = respaldos[opcion - 1]

    print(f"\nRespaldo seleccionado: {seleccionado}")

    confirmacion = input("¿Desea restaurarlo? (s/n): ").strip().lower()

    if confirmacion != "s":
        print("\nRestauración cancelada.")
        return

    exito, archivos, mensaje = restaurar_respaldo(seleccionado)

    if not exito:

        registrar_log(
            "RESTORE_ERROR",
            f"{seleccionado}: {mensaje}"
        )

        print(f"\nNo fue posible restaurar el respaldo: {mensaje}")
        return

    # Tras restaurar, las estructuras derivadas se reconstruyen
    # desde el CSV restaurado.

    generar_todos_los_indices(
        operacion="INDEX_REBUILD",
        motivo=f"Índices reconstruidos tras restaurar {seleccionado}"
    )

    generar_tabla_hash()

    registrar_log(
        "HASH_TABLE",
        f"Tabla hash reconstruida tras restaurar {seleccionado}"
    )

    registrar_log("RESTORE", f"Respaldo restaurado: {seleccionado}")

    pila_operaciones.push(f"RESTORE - {seleccionado}")

    print("\nRespaldo restaurado correctamente.")

    print("\nArchivos restaurados:")

    for archivo in archivos:
        print(f"- {archivo}")

    print("\nÍndices reconstruidos.")
    print("Tabla hash reconstruida.")

    # Los hashes NO se recalculan: se verifica el sistema
    # restaurado contra los hashes que venían en el respaldo.

    print("\nVerificación de integridad posterior a la restauración:")

    resultados = verificar_integridad()

    imprimir_resultados_integridad(resultados)

    if any(r["estado"] != "OK" for r in resultados):

        print(
            "\nAlgunos archivos no coinciden con los hashes "
            "registrados. Si confía en el estado actual, use la "
            "opción 14 para registrar los hashes nuevamente."
        )


# ---------------------------------------------------------------
# Menú
# ---------------------------------------------------------------

def mostrar_menu():

    configuracion = cargar_configuracion()

    titulo = str(configuracion.get("nombre_sistema", "SISTEMA")).upper()

    print("\n================================================")
    print(f" {titulo}")
    print(f" Versión {configuracion.get('version', '1.0')}")
    print("================================================")

    print("1. Registrar información")
    print("2. Mostrar todos los registros")
    print("3. Buscar por ID")
    print("4. Buscar por atributo")
    print("5. Actualizar registro")
    print("6. Eliminar registro")

    print("7. Mostrar índice principal")
    print("8. Mostrar índice invertido")
    print("9. Buscar utilizando índice")
    print("10. Reconstruir índices")

    print("11. Mostrar tabla hash")
    print("12. Buscar utilizando hashing")
    print("13. Mostrar colisiones")

    print("14. Registrar hashes de integridad")
    print("15. Verificar integridad de archivos")

    print("16. Consultar logs")

    print("17. Mostrar pila de operaciones")
    print("18. Consultar TOP de la pila")
    print("19. Retirar operación de la pila (POP)")

    print("20. Consultar metadatos")

    print("21. Exportar información a XML")

    print("22. Generar respaldo")
    print("23. Consultar respaldos")
    print("24. Restaurar respaldo")

    print("0. Salir")

    print("================================================")


ACCIONES = {
    "1": registrar_informacion,
    "2": mostrar_todos,
    "3": buscar_por_id,
    "4": buscar_por_atributo,
    "5": actualizar,
    "6": eliminar,
    "7": mostrar_indice_principal,
    "8": mostrar_indice_invertido,
    "9": buscar_utilizando_indice,
    "10": reconstruir_indices,
    "11": mostrar_tabla_hash,
    "12": buscar_utilizando_hash,
    "13": mostrar_colisiones,
    "14": registrar_integridad,
    "15": consultar_integridad,
    "16": consultar_logs,
    "17": mostrar_pila,
    "18": consultar_top,
    "19": retirar_operacion_pila,
    "20": consultar_metadatos,
    "21": exportar_informacion_xml,
    "22": generar_respaldo,
    "23": consultar_respaldos,
    "24": restaurar_desde_respaldo
}


def iniciar_sistema():
    """
    Prepara los archivos base y revisa el estado inicial.
    """

    crear_archivo_si_no_existe()
    preparar_log()
    cargar_configuracion()

    try:

        # Si ya existen hashes registrados, avisar si el CSV
        # fue modificado fuera del sistema.

        if cargar_hashes():

            for resultado in verificar_integridad():

                if resultado["estado"] == "ALTERADO":

                    print(
                        f"\n⚠ ADVERTENCIA: {resultado['archivo']} "
                        "fue modificado fuera del sistema."
                    )

                    registrar_log(
                        "INTEGRITY_CHECK",
                        f"{resultado['archivo']} -> ALTERADO (al iniciar)"
                    )

        asegurar_indices()
        cargar_tabla_hash()

    except ErrorFormatoCSV as error:

        print(f"\n⚠ {error}")
        print(
            "Puede restaurar un respaldo con la opción 24 "
            "o corregir el archivo manualmente."
        )

        registrar_log("ERROR", f"Formato incorrecto al iniciar: {error}")

    registrar_log("SYSTEM", "Inicio de ejecución del sistema")


def main():

    iniciar_sistema()

    while True:

        mostrar_menu()

        try:
            opcion = input("Seleccione una opción: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\n\nEntrada finalizada. Cerrando el sistema.")
            registrar_log("SYSTEM", "Cierre del sistema (entrada finalizada)")
            break

        if opcion == "0":

            registrar_log("SYSTEM", "Cierre normal del sistema")

            print("\nPrograma finalizado.")

            break

        accion = ACCIONES.get(opcion)

        if accion is None:
            print("\nOpción inválida.")
            continue

        try:
            accion()

        except (EOFError, KeyboardInterrupt):
            print("\n\nEntrada interrumpida. Cerrando el sistema.")
            registrar_log("SYSTEM", "Cierre del sistema (entrada interrumpida)")
            break

        except ErrorFormatoCSV as error:

            print(f"\nERROR de formato: {error}")

            registrar_log("ERROR", f"Formato incorrecto: {error}")

        except ValueError as error:

            print(f"\nERROR: {error}")

            registrar_log("ERROR", f"Dato inválido: {error}")

        except OSError as error:

            print(f"\nERROR de archivo: {error}")

            registrar_log("ERROR", f"Error de archivo: {error}")


if __name__ == "__main__":
    main()