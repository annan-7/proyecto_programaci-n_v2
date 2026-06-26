**Editor de Fondos para Imágenes Digitales**

**Descripción**
- **Resumen:** Herramienta simple para detectar objetos en una imagen (por muestreo de fondo en las esquinas) y reemplazar el fondo por imágenes alternativas.

**Requisitos**
- **Python:** 3.8 o superior.
- **Dependencias:** Instalar con pip:

```
pip install numpy pillow matplotlib
```

**Estructura del proyecto**
- **`main.py`:** Punto de entrada principal del proyecto. ([main.py](main.py))
- **`Fondos/`**: Carpeta donde deben colocarse las imágenes de fondo alternativas. ([Fondos](Fondos))
- **`Objetos/`**: Carpeta con las imágenes de objetos a procesar. ([Objetos](Objetos))
- **`resultados/`**: Carpeta de salida donde se guardan imágenes y reportes generados. ([resultados](resultados))

**Uso**
1. Coloque la(s) imagen(es) del objeto en la carpeta [Objetos](Objetos).
2. Coloque al menos 2 imágenes de fondo en [Fondos](Fondos).
3. Ejecute:

```
python main.py
```

4. En la consola seleccione la imagen principal (por número). Se abrirá una ventana con la interfaz gráfica.

**Interfaz (botones)**
- **Original:** Muestra la imagen original.
- **Fondo 1 / Fondo 2:** Muestra la imagen con el fondo reemplazado por cada alternativa.
- **Guardar:** Guarda la imagen mostrada actualmente en `resultados/` con marca de tiempo.
- **Reporte:** Genera un archivo `.txt` en `resultados/` con la cantidad y coordenadas de los píxeles detectados como objeto.

**Algoritmo (resumen técnico)**
- **Muestreo de fondo:** Toma los píxeles de las 4 esquinas y calcula su promedio como color de fondo.
- **Detección:** Calcula la distancia euclidiana por píxel entre la imagen y el color de fondo; aplica un umbral (por defecto 45.0) para obtener la máscara binaria del objeto.
- **Reemplazo de fondo:** Combina la imagen original y el fondo objetivo usando la máscara.

**Salida**
- Imágenes resultantes y reportes de píxeles en la carpeta [resultados](resultados). Los archivos incluyen un timestamp en su nombre.

**Errores comunes y soluciones**
- **Carpeta faltante:** Si `[Objetos]` o `[Fondos]` no existen, créelas y añada imágenes.
- **Pocos fondos:** Asegúrese de tener al menos 2 imágenes en `[Fondos]`.
- **Permisos/IO:** Verifique permisos de escritura para crear `resultados/`.


