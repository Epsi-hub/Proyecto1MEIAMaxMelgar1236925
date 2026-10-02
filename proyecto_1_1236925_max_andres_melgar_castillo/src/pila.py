class PilaOperaciones:

    def __init__(self):
        """
        Inicializa una pila vacía.
        """
        self.elementos = []


    def push(self, operacion):
        """
        Agrega una operación al TOP de la pila.
        """
        self.elementos.append(operacion)


    def pop(self):
        """
        Elimina y retorna la operación
        ubicada en el TOP.
        """

        if self.esta_vacia():
            return None

        return self.elementos.pop()


    def peek(self):
        """
        Retorna la operación ubicada en el TOP
        sin eliminarla.
        """

        if self.esta_vacia():
            return None

        return self.elementos[-1]


    def esta_vacia(self):
        """
        Verifica si la pila está vacía.
        """
        return len(self.elementos) == 0


    def tamanio(self):
        """
        Retorna la cantidad de elementos.
        """
        return len(self.elementos)


    def obtener_elementos(self):
        """
        Retorna los elementos desde el TOP
        hasta la operación más antigua.
        """
        return list(reversed(self.elementos))