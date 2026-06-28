#Hecho por : Matias Espinoza, Annan John

#El os y sys son necesarios para la gestión de archivos y errores.
import os
import sys
#Numpy y Matplotlib son esenciales para el procesamiento de imágenes y la interfaz gráfica.
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
#PIL (Pillow) se utiliza para la carga y manipulación de imágenes 
# y datetime para generar nombres de archivos únicos basados en la fecha y hora.
from PIL import Image
from datetime import datetime




# Diccionario que guarda el estado compartido entre las funciones
# de la interfaz gráfica (imágenes, máscara, ejes y referencias).
estado_gui = {
    "img_orig": None,
    "img_f1": None,
    "img_f2": None,
    "mascara": None,
    "img_actual": None,
    "titulo_actual": "",
    "im_display": None,
    "ax": None,
    "fig": None,
}


# 1. Funciones de Carga y procesamiento de Imágenes

def obtener_archivos_imagen(carpeta):
    # Lista los archivos de imagen válidos en una carpeta.
    extensiones_validas = ('.png', '.jpg', '.jpeg')
    try:
        if not os.path.exists(carpeta):
            raise FileNotFoundError(f"La carpeta '{carpeta}' no existe.")
        
        archivos = [f for f in os.listdir(carpeta) if f.lower().endswith(extensiones_validas)]
        if not archivos:
            raise ValueError(f"No se encontraron imágenes válidas en '{carpeta}'.")
        return sorted(archivos)
    except Exception as e:
        print(f"Error al leer la carpeta {carpeta}: {e}")
        sys.exit(1)

def seleccionar_imagen(archivos, titulo_mensaje):
    # Muestra un menú por consola y valida la elección del usuario.
    print(f"\n--- {titulo_mensaje} ---")
    for i, arch in enumerate(archivos):
        print(f"{i + 1}. {arch}")
    
    while True:
        try:
            opcion = int(input("Ingrese el número de la imagen que desea usar: "))
            if 1 <= opcion <= len(archivos):
                return archivos[opcion - 1]
            else:
                print("Número fuera de rango. Intente nuevamente.")
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número entero.")

def cargar_imagen_como_matriz(ruta):
    # Carga una imagen y la convierte a una matriz NumPy con forma (H, W, 3).
    try:
        img_pil = Image.open(ruta).convert('RGB')
        return np.array(img_pil)
    except Exception as e:
        raise IOError(f"No se pudo cargar la imagen {ruta}: {e}")

def redimensionar_matriz(matriz_img, alto_objetivo, ancho_objetivo):
    # Redimensiona la imagen con PIL y devuelve la matriz resultante.
    img_pil = Image.fromarray(matriz_img)
    img_resized = img_pil.resize((ancho_objetivo, alto_objetivo), Image.Resampling.LANCZOS)
    return np.array(img_resized)


# 2. Estragegias de Identificación del Objeto

def generar_mascara_objeto(matriz_img):
    alto, ancho, _ = matriz_img.shape

    # Paso 1: muestreo robusto del fondo.
    # Tomamos bandas de 5 píxeles en los cuatro bordes de la imagen.
    margen = 5
    bordes = np.concatenate([
        matriz_img[0:margen, :, :].reshape(-1, 3),
        matriz_img[alto-margen:alto, :, :].reshape(-1, 3),
        matriz_img[:, 0:margen, :].reshape(-1, 3),
        matriz_img[:, ancho-margen:ancho, :].reshape(-1, 3)
    ], axis=0)
    
    # Usamos la mediana para ser resistentes a valores atipicos
    color_fondo = np.median(bordes, axis=0)
    
  
    # Paso 2: calculamos la distancia euclidiana por pixel
    diferencia = matriz_img.astype(np.float32) - color_fondo.astype(np.float32)
    distancias = np.sqrt(np.sum(diferencia**2, axis=2))
    

    # Paso 3: umbral adaptativo (permisivo).
    # Usamos el percentil 60 para incluir más píxeles como objeto
    # y así priorizar no recortar parte del objeto.
    umbral_adaptativo = np.percentile(distancias, 60)
    umbral_final = max(umbral_adaptativo, 25.0)  # umbral mínimo de seguridad
    
    mascara = (distancias > umbral_final).astype(np.uint8)
    

    # Paso 4: limpieza de la máscara con closing (dilatacion + erosion suave)
    # Rellena huecos pequeños sin erosionar los bordes del objeto

    mascara = limpiar_mascara_closing(mascara)
    
    return mascara


def limpiar_mascara_closing(mascara):
    alto, ancho = mascara.shape
    kernel_size = 3
    pad = kernel_size // 2

    # Fase 1: dilatacion
    # Un pixel pasa a ser objeto si al menos 1 vecino lo es.
    # Esto ayuda a rellenar pequeños huecos dentro del objeto.
    padded = np.pad(mascara, pad, mode='constant', constant_values=0)
    suma_vecinos = np.zeros_like(mascara, dtype=np.int32)

    for i in range(kernel_size):
        for j in range(kernel_size):
            suma_vecinos += padded[i:i+alto, j:j+ancho]

    # En la dilatacion, si al menos 2 vecinos son objeto, marcamos el píxel.
    dilatada = (suma_vecinos >= 2).astype(np.uint8)

    # Fase 2: erosion suave
    # Conservamos un píxel si al menos 5 de 9 vecinos son objeto.
    # Esto reduce el ruido pero preserva los bordes del objeto.
    padded_dil = np.pad(dilatada, pad, mode='constant', constant_values=0)
    suma_vecinos_2 = np.zeros_like(dilatada, dtype=np.int32)

    for i in range(kernel_size):
        for j in range(kernel_size):
            suma_vecinos_2 += padded_dil[i:i+alto, j:j+ancho]

    # Erosion suave: se requiere al menos 5 vecinos para mantener el píxel.
    final = (suma_vecinos_2 >= 5).astype(np.uint8)

    return final


def reemplazar_fondo_matricial(img_original, mascara, img_fondo):

    #Reemplaza el fondo de una imagen usando una máscara binaria.

    # Paso 1: asegurar que la máscara sea estrictamente binaria
    mascara_binaria = np.clip(mascara, 0, 1).astype(np.uint8)

    # Expandir la máscara a 3 canales (H, W) a (H, W, 3)
    mascara_3d = np.stack([mascara_binaria] * 3, axis=2).astype(np.float32)

    # Paso 2: convertir imágenes a float32 para operación segura
    img_orig_f = img_original.astype(np.float32)
    img_fondo_f = img_fondo.astype(np.float32)

    # Paso 3: mezcla matricial segura entre objeto y fondo
    resultado = (img_orig_f * mascara_3d) + (img_fondo_f * (1.0 - mascara_3d))

    # Paso 4: recortar valores y convertir a uint8
    resultado = np.clip(resultado, 0, 255).astype(np.uint8)

    return resultado


# 3. GUARDADO Y REPORTES

def obtener_timestamp():
    # Devuelve una cadena con la fecha y hora actual para nombres únicos
    return datetime.now().strftime("%d%m%Y_%H%M%S")

def guardar_imagen_gui():
    #Guarda la imagen que está siendo mostrada en la interfaz.
    try:
        os.makedirs("resultados", exist_ok=True)
        nombre = f"imagen_{obtener_timestamp()}.png"
        ruta = os.path.join("resultados", nombre)
        
        img_pil = Image.fromarray(estado_gui["img_actual"])
        img_pil.save(ruta)
        print(f"Imagen guardada exitosamente: {ruta}")
    except Exception as e:
        print(f"Error al guardar la imagen: {e}")

def generar_reporte_txt():
    """Genera un archivo de texto con información sobre el objeto detectado.
    El reporte incluye la cantidad de píxeles detectados y sus coordenadas.
    """
    try:
        os.makedirs("resultados", exist_ok=True)
        nombre = f"reporte_{obtener_timestamp()}.txt"
        ruta = os.path.join("resultados", nombre)
        
        mascara = estado_gui["mascara"]
        filas, columnas = np.where(mascara == 1)
        cantidad_pixeles = len(filas)
        
        with open(ruta, 'w', encoding='utf-8') as archivo:
            archivo.write(f"Cantidad de píxeles del objeto: {cantidad_pixeles}\n")
            archivo.write("Coordenadas:\n")
            
            for i in range(cantidad_pixeles):
                archivo.write(f"({filas[i]},{columnas[i]}) ")
                if (i + 1) % 15 == 0:
                    archivo.write("\n")
                    
        print(f"Reporte generado exitosamente: {ruta}")
    except Exception as e:
        print(f"Error al generar el reporte: {e}")


# 4. Funciones de Interfaz Gráfica {Matplotlib}

def actualizar_pantalla():
    #Actualiza la imagen y el título mostrados en la figura de Matplotlib.
    estado_gui["im_display"].set_data(estado_gui["img_actual"])
    estado_gui["ax"].set_title(estado_gui["titulo_actual"], fontsize=14, fontweight='bold')
    estado_gui["fig"].canvas.draw_idle()

def mostrar_orig(event):
    #Callback para mostrar la imagen original.
    estado_gui["img_actual"] = estado_gui["img_orig"]
    estado_gui["titulo_actual"] = "Imagen Original"
    actualizar_pantalla()

def mostrar_f1(event):
    #Callback para mostrar la imagen con el primer fondo alternativo.
    estado_gui["img_actual"] = estado_gui["img_f1"]
    estado_gui["titulo_actual"] = "Imagen con Fondo Alternativo 1"
    actualizar_pantalla()

def mostrar_f2(event):
    #Callback para mostrar la imagen con el segundo fondo alternativo.
    estado_gui["img_actual"] = estado_gui["img_f2"]
    estado_gui["titulo_actual"] = "Imagen con Fondo Alternativo 2"
    actualizar_pantalla()

def accion_guardar(event):
    #Callback del botón 'Guardar' (guarda la imagen mostrada).
    guardar_imagen_gui()

def accion_reporte(event):
    #Callback del botón 'Reporte' (genera el archivo de texto).
    generar_reporte_txt()

def crear_interfaz():
    #Construye la ventana de Matplotlib con los botones de control.
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.subplots_adjust(bottom=0.2)
    
    # Guardamos referencias útiles en el estado global
    estado_gui["fig"] = fig
    estado_gui["ax"] = ax
    estado_gui["img_actual"] = estado_gui["img_orig"]
    estado_gui["titulo_actual"] = "Imagen Original"
    
    im_display = ax.imshow(estado_gui["img_actual"])
    ax.set_title(estado_gui["titulo_actual"], fontsize=14, fontweight='bold')
    ax.axis('off')
    estado_gui["im_display"] = im_display
    
    # Posiciones de los botones: [left, bottom, width, height]
    ax_orig = plt.axes([0.02, 0.05, 0.15, 0.075])
    ax_f1   = plt.axes([0.20, 0.05, 0.15, 0.075])
    ax_f2   = plt.axes([0.38, 0.05, 0.15, 0.075])
    ax_save = plt.axes([0.56, 0.05, 0.15, 0.075])
    ax_rep  = plt.axes([0.74, 0.05, 0.15, 0.075])
    
    # Crear y vincular los botones a sus callbacks
    btn_orig = Button(ax_orig, 'Original')
    btn_f1 = Button(ax_f1, 'Fondo 1')
    btn_f2 = Button(ax_f2, 'Fondo 2')
    btn_save = Button(ax_save, 'Guardar')
    btn_rep = Button(ax_rep, 'Reporte')
    
    btn_orig.on_clicked(mostrar_orig)
    btn_f1.on_clicked(mostrar_f1)
    btn_f2.on_clicked(mostrar_f2)
    btn_save.on_clicked(accion_guardar)
    btn_rep.on_clicked(accion_reporte)
    
    # IMPORTANTE: Matplotlib necesita que mantengamos referencias a los botones
    estado_gui["botones"] = [btn_orig, btn_f1, btn_f2, btn_save, btn_rep]


# 5. Ejecución Principal

def main():
    print("Iniciando editor de fondos para imágenes digitales...")
    
    try:
        # 1. Cargar listas de archivos
        objetos = obtener_archivos_imagen("Objetos")
        fondos = obtener_archivos_imagen("Fondos")
        
        if len(fondos) < 2:
            raise ValueError("La carpeta 'Fondos/' debe contener al menos 2 imágenes.")
        
        # 2. Selección de Imagen Principal
        arch_objeto = seleccionar_imagen(objetos, "Seleccione la IMAGEN PRINCIPAL (Objeto)")
        ruta_objeto = os.path.join("Objetos", arch_objeto)
        
        # 3. Selección Automática de Fondos
        arch_fondo1 = fondos[0]
        arch_fondo2 = fondos[1]
        print(f"\nFondos alternativos seleccionados automáticamente: '{arch_fondo1}' y '{arch_fondo2}'")
        
        # 4. Carga y Procesamiento de Matrices
        print("\n Procesando imágenes...")
        matriz_orig = cargar_imagen_como_matriz(ruta_objeto)
        alto, ancho, _ = matriz_orig.shape
        
        matriz_f1 = redimensionar_matriz(cargar_imagen_como_matriz(os.path.join("Fondos", arch_fondo1)), alto, ancho)
        matriz_f2 = redimensionar_matriz(cargar_imagen_como_matriz(os.path.join("Fondos", arch_fondo2)), alto, ancho)
        
        # 5. Identificación del Objeto
        mascara = generar_mascara_objeto(matriz_orig)
        
        # 6. Reemplazo de Fondos
        resultado_f1 = reemplazar_fondo_matricial(matriz_orig, mascara, matriz_f1)
        resultado_f2 = reemplazar_fondo_matricial(matriz_orig, mascara, matriz_f2)
        
        print("Procesamiento matricial completado.")
        
        # 7. Preparar estado global para la GUI
        estado_gui["img_orig"] = matriz_orig
        estado_gui["img_f1"] = resultado_f1
        estado_gui["img_f2"] = resultado_f2
        estado_gui["mascara"] = mascara
        
        # 8. Lanzar Interfaz Gráfica
        crear_interfaz()
        plt.show()
        
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")
    except Exception as e:
        print(f"\n ERROR INESPERADO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
