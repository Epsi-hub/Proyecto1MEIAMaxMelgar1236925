# Proyecto #1
## Sistema Integral de Gestión y Recuperación de Información basado en Archivos

Curso: Manejo e Implementación de Archivos

---

## Descripción

Este proyecto implementa un sistema de gestión de información utilizando archivos como mecanismo principal de almacenamiento.

El sistema permite aplicar diferentes conceptos relacionados con el manejo e implementación de archivos, incluyendo:

- Persistencia utilizando CSV.
- Configuración mediante JSON.
- Exportación de información a XML.
- Operaciones CRUD.
- Búsqueda secuencial.
- Índices.
- Índices invertidos.
- Organización multillave.
- Hashing.
- Manejo de colisiones.
- Integridad mediante SHA-256.
- Logs.
- Pilas LIFO.
- Metadatos.
- Respaldos y restauración.

El sistema no utiliza una base de datos como mecanismo principal de almacenamiento.

---

# Requisitos

Para ejecutar el proyecto se necesita:

- Python 3
- Visual Studio Code
- Git
- Git Bash

No es necesario instalar librerías externas.

---

# Clonar el repositorio

Desde Git Bash:

```bash
git clone URL_DEL_REPOSITORIO
```

Ingresar a la carpeta:

```bash
cd Proyecto_1
```

---

# Ejecutar el sistema

Desde la raíz del proyecto:

```bash
python main.py
```

También puede utilizarse:

```bash
python3 main.py
```

dependiendo de la configuración del equipo.

---

# Estructura del proyecto

```text
Proyecto_1/
│
├── main.py
├── README.md
├── .gitignore
│
├── data/
│   └── registros.csv
│
├── config/
│   └── configuracion.json
│
├── indices/
│   ├── indice_id.json
│   ├── indice_categoria.json
│   ├── indice_estado.json
│   ├── tabla_hash.json
│   └── hashes.json
│
├── exports/
│   └── registros.xml
│
├── logs/
│   └── sistema.log
│
├── backups/
│
├── src/
│   ├── __init__.py
│   ├── archivos.py
│   ├── busquedas.py
│   ├── indices.py
│   ├── hashing.py
│   ├── integridad.py
│   ├── logs.py
│   ├── metadatos.py
│   ├── pila.py
│   └── respaldos.py
│
└── documentacion/
```

---

# Archivo principal

El archivo principal utilizado para almacenar la información es:

```text
data/registros.csv
```

Los registros poseen la siguiente estructura:

```text
id
nombre
categoria
descripcion
fecha
estado
```

---

# Configuración

La configuración general se encuentra en:

```text
config/configuracion.json
```

Este archivo utiliza formato JSON para almacenar parámetros relacionados con el sistema.

---

# Índices

Los índices generados por el sistema se almacenan en:

```text
indices/
```

Entre ellos se encuentran:

```text
indice_id.json
indice_categoria.json
indice_estado.json
```

Estos archivos permiten representar diferentes mecanismos de organización y recuperación de información.

---

# Hashing

El sistema implementa una tabla hash para organizar los identificadores de los registros.

La tabla generada se almacena en:

```text
indices/tabla_hash.json
```

La implementación contempla el manejo de colisiones.

---

# Integridad

El sistema utiliza:

```text
SHA-256
```

para verificar la integridad de archivos importantes.

Los hashes registrados se almacenan en:

```text
indices/hashes.json
```

---

# Logs

Las operaciones realizadas por el sistema quedan registradas en:

```text
logs/sistema.log
```

El archivo permite consultar el historial persistente de diferentes operaciones realizadas.

---

# Pila de operaciones

Durante la ejecución se utiliza una estructura:

```text
LIFO
Last In - First Out
```

para mantener un historial temporal de operaciones.

La pila existe únicamente durante la ejecución del programa.

---

# Metadatos

El sistema permite consultar información de los archivos, incluyendo:

- Nombre.
- Ruta.
- Extensión.
- Tamaño.
- Fecha de creación.
- Fecha de modificación.
- Permisos.

---

# Exportación XML

Los registros almacenados en CSV pueden exportarse a:

```text
exports/registros.xml
```

El archivo XML representa la información existente al momento de realizar la exportación.

---

# Respaldos

Los respaldos generados por el sistema se almacenan en:

```text
backups/
```

Cada respaldo utiliza una carpeta identificada mediante fecha y hora.

Ejemplo:

```text
backup_20260925_153000/
```

El sistema también permite restaurar información utilizando un respaldo existente.

Después de una restauración se reconstruyen las estructuras auxiliares necesarias.

---

# Menú principal

El sistema presenta las siguientes operaciones:

```text
1. Registrar información
2. Mostrar todos los registros
3. Buscar por ID
4. Buscar por atributo
5. Actualizar registro
6. Eliminar registro
7. Mostrar índice principal
8. Mostrar índice invertido
9. Buscar utilizando índice
10. Reconstruir índices
11. Mostrar tabla hash
12. Buscar utilizando hashing
13. Mostrar colisiones
14. Registrar hashes de integridad
15. Verificar integridad de archivos
16. Consultar logs
17. Mostrar pila de operaciones
18. Consultar TOP de la pila
19. Retirar operación de la pila (POP)
20. Consultar metadatos
21. Exportar información a XML
22. Generar respaldo
23. Consultar respaldos
24. Restaurar respaldo
0. Salir
```

---

# Consideraciones

Los archivos generados por el sistema pueden cambiar durante la ejecución.

Algunas estructuras, como los índices y la tabla hash, pueden reconstruirse utilizando la información almacenada en el archivo principal.

Los estudiantes deberán analizar el código fuente para comprender cómo se implementa cada mecanismo.

---

# Preguntas de análisis
1. ¿Cuál es el archivo principal utilizado para persistir la información?
Se utiliza registros.csv, en él se guardan los datos inicialmente
2. ¿Qué diferencia existe entre el archivo CSV y el archivo XML generado?
CSV es la forma de  almacenamiento principal, el XML es una transformación de los datos .csv, a nivel práctico, se diferencian en estructura (XML se rige en etiquetas, CSV tiene un estándar más tabular)
3. ¿Cómo funciona la búsqueda secuencial?
Recorre fila por fila hasta encontrar el ID o terminar.
4. ¿Qué ventaja ofrece un índice frente a recorrer todos los registros?
Lee solo la fila necesaria, no todo el archivo, lo que ahora recursos y mejora la eficiencia.
5. ¿Qué información contiene el índice invertido?
Relaciona cada valor de atributo con su lista de IDs.
6. ¿Cómo se implementa la organización multillave?
Con varios índices en paralelo que se intersectan al buscar.
7. ¿Qué función hash utiliza el sistema?
id módulo 10 (tamaño de tabla)
8. ¿Por qué pueden producirse colisiones?
Claves distintas pueden dar la misma posición (ej: 01 y 101 modulo 10 dan la misma posición, osea 1)
9. ¿Cómo se resuelven las colisiones?
Encadenamiento, cada posición guarda una lista enlazada.
10. ¿Qué propósito tiene SHA-256 dentro del sistema?
Se usa para crear  la huella usada para detectar si un archivo fue alterado.
11. ¿Qué diferencia existe entre el log y la pila de operaciones?
Log es historial completo; pila guarda operaciones LIFO.
12. ¿Por qué la pila desaparece cuando termina la ejecución?
Desaparece porque la pila esta en la ram
13. ¿Qué metadatos pueden obtenerse de un archivo?
Se pueden obtener datos como nombre, ruta, tamaño, extensión, fechas y permisos.
14. ¿Qué archivos deben considerarse información principal y cuáles son estructuras derivadas?
El archivo principal es CSV, los derivados son los indices, hashes, logs, pila, XML.
15. ¿Por qué se reconstruyen los índices después de restaurar un respaldo?
Porque las posiciones cambian y deben quedar coherentes.