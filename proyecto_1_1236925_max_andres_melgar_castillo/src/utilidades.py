from datetime import datetime


def validar_id(valor):
    """
    Retorna un mensaje de error o None si el ID es válido.
    El ID debe ser numérico porque la función hash
    utiliza el residuo de una división entera.
    """

    valor = (valor or "").strip()

    if not valor:
        return "El ID no puede estar vacío."

    if not (valor.isascii() and valor.isdigit()):
        return "El ID debe ser numérico (solo dígitos)."

    return None


def validar_fecha(valor):
    """
    Retorna un mensaje de error o None si la fecha
    tiene el formato AAAA-MM-DD y es una fecha real.
    """

    valor = (valor or "").strip()

    mensaje = "La fecha debe tener el formato AAAA-MM-DD."

    if len(valor) != 10:
        return mensaje

    try:
        datetime.strptime(valor, "%Y-%m-%d")
    except ValueError:
        return mensaje

    return None


def validar_texto(valor, nombre_campo):
    """
    Retorna un mensaje de error o None si el texto
    no está vacío ni contiene saltos de línea.
    """

    valor = (valor or "").strip()

    if not valor:
        return f"{nombre_campo} no puede estar vacío."

    if "\n" in valor or "\r" in valor:
        return f"{nombre_campo} no puede contener saltos de línea."

    return None


def validar_registro(registro):
    """
    Valida todos los campos de un registro.
    Retorna una lista con los errores encontrados
    (lista vacía si el registro es válido).
    """

    errores = []

    validaciones = [
        validar_id(registro.get("id")),
        validar_texto(registro.get("nombre"), "El nombre"),
        validar_texto(registro.get("categoria"), "La categoría"),
        validar_texto(registro.get("descripcion"), "La descripción"),
        validar_fecha(registro.get("fecha")),
        validar_texto(registro.get("estado"), "El estado")
    ]

    for error in validaciones:
        if error:
            errores.append(error)

    return errores