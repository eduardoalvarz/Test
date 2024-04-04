import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
pd.options.mode.chained_assignment = None

def cargar_base_datos(rutas_licores):
    # Lista para almacenar los DataFrames de los licores
    licores_dfs = []

    # Cargar los DataFrames de los licores
    for ruta in rutas_licores:
        df = pd.read_csv(ruta)
        licores_dfs.append(df)

    # Unir todos los DataFrames de los licores en uno solo
    bebidas_df = pd.concat(licores_dfs)
    bebidas_df.reset_index(drop=True, inplace=True)

    return bebidas_df

def procesar_base_datos(bebidas_df):
    # Filtrar solo los datos donde 'Periodo' es igual a 'MES'
    bebidas_df = bebidas_df[bebidas_df['Periodo'] == 'MES']

    # Convertir la columna 'Fecha' a formato de fecha
    bebidas_df['Fecha'] = pd.to_datetime(bebidas_df['Fecha'], format='%d/%m/%Y')
    bebidas_df['AÑO'] = bebidas_df['Fecha'].dt.year
    bebidas_df['MES'] = bebidas_df['Fecha'].dt.month

    # Eliminar columnas innecesarias
    columns_to_drop = ['Contml', 'Graduación', 'Segmento', 'SubMarcaEsp', 'Presentación', 'BandaPrecio']
    bebidas_df.drop(columns=columns_to_drop, inplace=True)

    return bebidas_df

def generar_nuevas_filas(bebidas_df):
    # Crear una base de datos vacía con la misma estructura
    bebidas_empty_df = pd.DataFrame(columns=bebidas_df.columns)

    # Obtener listas de marcas, regiones y años únicos
    marcas = bebidas_df['Marca'].unique()
    regiones = bebidas_df['Region'].unique()
    años = bebidas_df['AÑO'].unique()

    # Crear nuevas filas para cada combinación de marca, región y año
    new_rows = []
    for marca in marcas:
        for region in regiones:
            for año in años:
                new_rows.append({'Marca': marca, 'Region': region, 'AÑO': año})

    return new_rows

def asignar_categorias_nuevas_filas(new_rows, bebidas_df):
    # Mapear cada marca a su categoría correspondiente
    categorias_por_marca = {}
    for categoria in bebidas_df['Categoria'].unique():
        marcas_categoria = bebidas_df[bebidas_df['Categoria'] == categoria]['Marca'].unique()
        for marca in marcas_categoria:
            categorias_por_marca[marca] = categoria

    # Asignar la categoría correcta a cada marca en las nuevas filas
    for row in new_rows:
        marca = row['Marca']
        if marca in categorias_por_marca:
            row['Categoria'] = categorias_por_marca[marca]

def procesar_licores(rutas_licores):
    # Cargar las bases de datos de los licores
    bebidas_df = cargar_base_datos(rutas_licores)

    # Procesar las bases de datos
    bebidas_df = procesar_base_datos(bebidas_df)

    # Generar nuevas filas para cada combinación de marca, región y año
    new_rows = generar_nuevas_filas(bebidas_df)

    # Asignar categorías a las nuevas filas
    asignar_categorias_nuevas_filas(new_rows, bebidas_df)

    # Crear un DataFrame con las nuevas filas
    bebidas_empty_df = pd.DataFrame(new_rows)

    # Agregar columnas 'CajasVirt' y 'Venta' con valor 0 para evitar NaN
    bebidas_empty_df['CajasVirt'] = 0
    bebidas_empty_df['Venta'] = 0

    # Unir las bases de datos con y sin datos
    bebidas_full_df = pd.concat([bebidas_df, bebidas_empty_df])
    bebidas_full_df.reset_index(drop=True, inplace=True)

    return bebidas_full_df

def guardar_base_datos(bebidas_df, ruta_archivo_csv):
    if ruta_archivo_csv:
        try:
            bebidas_df.to_csv(ruta_archivo_csv, index=False)
            messagebox.showinfo("Éxito", f"La base de datos se ha guardado en: {ruta_archivo_csv}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Función para cargar las bases de datos seleccionadas
def cargar_bases_datos():
    rutas_licores = [archivo.replace('"', '') for archivo in listbox.get(0, tk.END)]
    if not rutas_licores:
        messagebox.showerror("Error", "No se han seleccionado bases de datos.")
        return

    try:
        bebidas_df = procesar_licores(rutas_licores)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    return bebidas_df

# Función para seleccionar la ruta y el nombre del archivo de salida
def seleccionar_ruta_salida():
    bebidas_df = cargar_bases_datos()
    if bebidas_df is not None:
        ruta_archivo_csv = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
            title="Guardar base de datos"
        )
        guardar_base_datos(bebidas_df, ruta_archivo_csv)

# Función para abrir el cuadro de diálogo de selección de archivos
def seleccionar_archivos():
    rutas_licores = filedialog.askopenfilenames(title="Seleccionar bases de datos")
    for ruta in rutas_licores:
        listbox.insert(tk.END, f'"{ruta}"')

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Procesador de Bases de Datos")

# Crear el label y la lista para seleccionar las bases de datos
label = tk.Label(ventana, text="Selecciona bases de datos:")
label.pack()
listbox = tk.Listbox(ventana, selectmode=tk.MULTIPLE, width=50)
listbox.pack()

# Crear el botón para seleccionar archivos
boton_seleccionar = tk.Button(ventana, text="Seleccionar archivos", command=seleccionar_archivos)
boton_seleccionar.pack()

# Crear el botón para procesar las bases de datos y seleccionar la ruta de salida
boton_guardar = tk.Button(ventana, text="Generar | Guardar", command=seleccionar_ruta_salida)
boton_guardar.pack()

# Iniciar el bucle principal de la aplicación
ventana.mainloop()