CORRECION DE ACTIVIDADES

El código se encarga de corregir y recolectar resultados de actividades de estudiantes en un repositorio, en la versión subida se busca específicamente para la actividad "AB". A continuación, se proporciona una descripción general del código, su funcionamiento y cómo se utiliza.

Descripción
El código tiene como objetivo principal automatizar la corrección y recolección de resultados para una actividad de estudiantes en un repositorio. Realiza las siguientes tareas:

Corrección de Actividades (corrector_de_actividades):

Busca en el repositorio de cada estudiante el archivo especificado (archivo_a_buscar), que en este caso es "yolanda.py".
Copia los archivos de prueba (archivos_a_agregar) a la carpeta del estudiante si se encuentra el archivo buscado.
Ejecuta pruebas unitarias en los archivos de prueba en cada carpeta de estudiante y registra los resultados en un archivo de Excel (resultados.xlsx).
Recolección de Resultados (recolectar_resultados):

Recolecta los archivos de resultados generados por la corrección para cada estudiante y los mueve a una carpeta llamada "resultados AB".
Funciones Auxiliares:

agregar_archivo: Copia un archivo específico a una ubicación especificada.
Instrucciones de Uso
Asegúrate de tener todos los archivos de prueba y recursos necesarios en el directorio donde se encuentra este script.

Abre una terminal y navega hasta el directorio que contiene el script.

Ejecuta el script utilizando el intérprete de Python en un entorno WSL (Windows Subsystem for Linux) o en un entorno Linux. Por ejemplo:

python3 corrector.py

El script ejecutará la corrección de actividades para la actividad "AB", registrando los resultados en un archivo de Excel llamado resultados.xlsx. También recolectará los archivos de resultados generados y los moverá a una carpeta llamada "resultados AB".

Requisitos
Python 3.x instalado en tu sistema.
Los archivos de prueba y otros recursos necesarios deben estar presentes en el mismo directorio que el script.
Notas
Asegúrate de haber respaldado tus datos importantes antes de usar este script, ya que puede realizar cambios en los archivos y carpetas de los estudiantes.
Si deseas corregir una actividad diferente, asegúrate de ajustar los valores de actividad y archivo_a_buscar en el script.