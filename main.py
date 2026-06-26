import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from PIL import Image
from datetime import datetime


# Este diccionario mantiene el estado compartido entre las funciones de la GUI.
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


# 1. FUNCIONES DE CARGA Y VALIDACIÓN

def obtener_archivos_imagen(carpeta):
    """Lista archivos de imagen válidos en una carpeta."""
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
    """Muestra un menú en consola y valida la entrada del usuario."""
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
    """Carga una imagen y la convierte en una matriz NumPy (H, W, 3)."""
    try:
        img_pil = Image.open(ruta).convert('RGB')
        return np.array(img_pil)
    except Exception as e:
        raise IOError(f"No se pudo cargar la imagen {ruta}: {e}")

def redimensionar_matriz(matriz_img, alto_objetivo, ancho_objetivo):
    """Redimensiona la imagen usando PIL y devuelve la matriz."""
    img_pil = Image.fromarray(matriz_img)
    img_resized = img_pil.resize((ancho_objetivo, alto_objetivo), Image.Resampling.LANCZOS)
    return np.array(img_resized)


# 2. ESTRATEGIA DE IDENTIFICACIÓN (MATRICES)

def generar_mascara_objeto(matriz_img):
    """
    ESTRATEGIA: Muestreo de fondo en esquinas y Distancia Euclidiana.
    """
    alto, ancho, canales = matriz_img.shape
    
    # 1. Muestreo de esquinas
    esquinas = np.array([
        matriz_img[0, 0],
        matriz_img[0, ancho - 1],
        matriz_img[alto - 1, 0],
        matriz_img[alto - 1, ancho - 1]
    ])
    color_fondo = np.mean(esquinas, axis=0)
    
    # 2. Distancia euclidiana vectorizada
    diferencia = matriz_img.astype(np.float32) - color_fondo.astype(np.float32)
    distancias = np.sqrt(np.sum(diferencia**2, axis=2))
    
    # 3. Aplicación de Umbral
    umbral = 45.0
    mascara = (distancias > umbral).astype(np.uint8)
    
    return mascara

def reemplazar_fondo_matricial(img_original, mascara, img_fondo):
    """Reemplaza el fondo usando operaciones matriciales."""
    mascara_3d = np.stack([mascara] * 3, axis=2)
    resultado = (img_original * mascara_3d + img_fondo * (1 - mascara_3d))
    return resultado.astype(np.uint8)


# 3. GUARDADO Y REPORTES

def obtener_timestamp():
    return datetime.now().strftime("%d%m%Y_%H%M%S")

def guardar_imagen_gui():
    """Guarda la imagen actualmente visualizada."""
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
    """Genera un archivo .txt con la información del objeto detectado."""
    try:
        os.makedirs("resultados", exist_ok=True)
        nombre = f"reporte_{obtener_timestamp()}.txt"
        ruta = os.path.join("resultados", nombre)
        
        mascara = estado_gui["mascara"]
        filas, columnas = np.where(mascara == 1)
        cantidad_pixeles = len(filas)
        
        with open(ruta, 'w', encoding='utf-8') as archivo:
            archivo.write(f"Cantidad de píxeles del objeto: {cantidad_pixeles}\n")
            archivo.write("Coordenadas (fila, columna):\n")
            
            for i in range(cantidad_pixeles):
                archivo.write(f"({filas[i]},{columnas[i]}) ")
                if (i + 1) % 15 == 0:
                    archivo.write("\n")
                    
        print(f"Reporte generado exitosamente: {ruta}")
    except Exception as e:
        print(f"Error al generar el reporte: {e}")


# 4. FUNCIONES DE LA INTERFAZ GRÁFICA

def actualizar_pantalla():
    """Refresca la imagen mostrada en el eje de Matplotlib."""
    estado_gui["im_display"].set_data(estado_gui["img_actual"])
    estado_gui["ax"].set_title(estado_gui["titulo_actual"], fontsize=14, fontweight='bold')
    estado_gui["fig"].canvas.draw_idle()

def mostrar_orig(event):
    """Callback del botón 'Original'."""
    estado_gui["img_actual"] = estado_gui["img_orig"]
    estado_gui["titulo_actual"] = "Imagen Original"
    actualizar_pantalla()

def mostrar_f1(event):
    """Callback del botón 'Fondo 1'."""
    estado_gui["img_actual"] = estado_gui["img_f1"]
    estado_gui["titulo_actual"] = "Imagen con Fondo Alternativo 1"
    actualizar_pantalla()

def mostrar_f2(event):
    """Callback del botón 'Fondo 2'."""
    estado_gui["img_actual"] = estado_gui["img_f2"]
    estado_gui["titulo_actual"] = "Imagen con Fondo Alternativo 2"
    actualizar_pantalla()

def accion_guardar(event):
    """Callback del botón 'Guardar'."""
    guardar_imagen_gui()

def accion_reporte(event):
    """Callback del botón 'Reporte'."""
    generar_reporte_txt()

def crear_interfaz():
    """Construye la ventana de Matplotlib con sus botones."""
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.subplots_adjust(bottom=0.2)
    
    # Guardamos referencias en el estado global
    estado_gui["fig"] = fig
    estado_gui["ax"] = ax
    estado_gui["img_actual"] = estado_gui["img_orig"]
    estado_gui["titulo_actual"] = "Imagen Original"
    
    im_display = ax.imshow(estado_gui["img_actual"])
    ax.set_title(estado_gui["titulo_actual"], fontsize=14, fontweight='bold')
    ax.axis('off')
    estado_gui["im_display"] = im_display
    
    # Posiciones de los botones [left, bottom, width, height]
    ax_orig = plt.axes([0.02, 0.05, 0.15, 0.075])
    ax_f1   = plt.axes([0.20, 0.05, 0.15, 0.075])
    ax_f2   = plt.axes([0.38, 0.05, 0.15, 0.075])
    ax_save = plt.axes([0.56, 0.05, 0.15, 0.075])
    ax_rep  = plt.axes([0.74, 0.05, 0.15, 0.075])
    
    # Creación y vinculación de botones
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
    
    # IMPORTANTE: Matplotlib requiere mantener referencias vivas a los botones
    estado_gui["botones"] = [btn_orig, btn_f1, btn_f2, btn_save, btn_rep]


# 5. EJECUCIÓN PRINCIPAL

def main():
    print("Iniciando Editor de Fondos para Imágenes Digitales...")
    
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
        print("\nProcesando imágenes...")
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
        print(f"\nERROR INESPERADO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()