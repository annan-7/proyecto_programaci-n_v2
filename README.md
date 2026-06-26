Editor de Fondos para Imágenes Digitales

> Herramienta en Python para detectar objetos en imágenes y reemplazar su fondo de forma automática, con una interfaz gráfica interactiva.


  ¿Qué hace este proyecto?

Dado una imagen de un objeto sobre un fondo uniforme, el programa:

1. Detecta automáticamente el fondo, mostreando los píxeles de las 4 esquinas.
2. Segmenta el objeto, usando distancia euclidiana y un umbral de color.
3. Reemplaza el fondo con cualquiera de las imágenes alternativas disponibles.
4. Muestra el resultado en una interfaz gráfica con botones para navegar, guardar y generar reportes.

____________________________________________________________________________________________________________________________________
 
  - Requisitos

- Python 3.8 o superior
- Las siguientes librerías (instalables con pip):
  numpy
  pillow
  matplotlib


_____________________________________________________________________________________________________________________________________

  - Estructura del proyecto_programacion_v2


- main.py        -->    Script principal
- Objetos        -->    Coloca en esta carpeta las imágenes de los objetos a procesar
- Fondos         -->    Coloca en esta carpeta al menos 2 imágenes de fondo alternativas
- resultados     -->    Se genera en esta carpeta automáticamente al guardar imágenes o reportes

_____________________________________________________________________________________________________________________________________
  - Uso
 1. Preparar las carpetas
- Añade la imagen de tu objeto (con fondo simple) en la carpeta Objetos.
- Añade al menos 2 imágenes de fondo en la carpeta Fondos.

 2. Ejecutar el programa
- python main.py

 3. Seleccionar imagen
- En la consola aparecerá un menú numerado. Escribe el número de la imagen que quieras procesar y presiona Enter.

  4. Usar la interfaz gráfica
- Se abrirá una ventana con la imagen procesada y 5 botones:
-  Original    -->    Muestra la imagen sin modificar .
-  Fondo 1     -->    Muestra la imagen con el primer fondo alternativo.
-  Fondo 2     -->    Muestra la imagen con el segundo fondo alternativo.
-  Guardar     -->    Guarda la imagen actualmente visible en la carpeta resultados.
-  Reporte     -->    Genera un archivo de texto con las coordenadas de los píxeles detectados como objeto.

_______________________________________________________________________________________________________________________________________

   - Cómo funciona el algoritmo


1. Imagen original
      
2. Muestreo de las 4 esquinas → Color promedio del fondo
      
3. Distancia euclidiana píxel a píxel vs. color de fondo

4. Umbral (45.0) → Máscara binaria del objeto
      
5. Combinación matricial: objeto original + fondo nuevo
      
6. Imagen resultante


- Muestreo de esquinas: Se promedian los píxeles de las 4 esquinas para estimar el color del fondo.
- Distancia euclidiana: Para cada píxel se calcula √((R₁-R₂)² + (G₁-G₂)² + (B₁-B₂)²) respecto al color del fondo.
- Umbral: Los píxeles con distancia mayor a 45.0 se consideran parte del objeto.
- Reemplazo: Se aplica la máscara para combinar el objeto original con el fondo elegido.

> Nota: El algoritmo funciona mejor con imágenes que tienen un fondo de color uniforme o poco saturado.

_______________________________________________________________________________________________________________________________________

   - Archivos de salida

Los archivos generados se guardan en la carpetaresultados con un timestamp en el nombre:
- `imagen_DDMMAAAA_HHMMSS.png` — imagen exportada desde la GUI.
- `reporte_DDMMAAAA_HHMMSS.txt` — cantidad total de píxeles del objeto y sus coordenadas (fila, columna).

__________________________________________________________________________________________________________________________________

   - Problemas comunes

- Problema.                        -->    Solución.
- La carpeta 'Objetos' no existe.             -->  Crea la carpeta y añade al menos una imagen. 
- La carpeta 'Fondos' no existe.             -->  Crea la carpeta y añade al menos dos imágenes.
- Debe contener al menos 2 imágenes.            -->  Añade una segunda imagen a 'Fondos'.
- El objeto no se detecta bien.                -->  Prueba con imágenes que tengan un fondo más uniforme.
- Error de permisos en la carpeta 'Resultados'.   -->  Asegúrate de tener permisos de escritura en el directorio del proyecto.

__________________________________________________________________________________________________________________________________

  - Tecnologías usadas

- NumPy (https://numpy.org/) — operaciones matriciales para la segmentación
- Pillow (https://python-pillow.org/) — carga, conversión y guardado de imágenes
- Matplotlib (https://matplotlib.org/) — visualización e interfaz gráfica con botones
__________________________________________________________________________________________________________________________________

   - Licencia

Este proyecto fue desarrollado con fines académicos. Puedes usarlo y modificarlo libremente.
