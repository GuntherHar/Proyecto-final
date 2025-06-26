import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk  # Import ttk for Progressbar
from PIL import Image, ImageTk
import networkx as nx
from collections import deque
import matplotlib.pyplot as plt
import json
from graphviz import Digraph # Asegúrate de que graphviz esté instalado y en tu PATH
import io
import os

# Importaciones para Concurrencia
import queue
import threading
import time
import random

class Grafo:
    def __init__(self):
        self.atributos = {}
        self.graph = nx.DiGraph() # Store the networkx graph as an instance variable
        self.nodes_in_graph = [] # To store the list of node strings generated

    def leerJSON(self, ruta_archivo):
        peliculas = {}
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                peliculas = json.load(f)
                return peliculas
        except FileNotFoundError:
            messagebox.showerror("Error de Archivo", f"El archivo '{ruta_archivo}' no se encontró.")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Error JSON", f"El archivo '{ruta_archivo}' tiene un formato JSON inválido.")
            return {}

    def crearNodo(self, peliculas):
        # Clears existing nodes before creation (useful if you recreate graph)
        self.nodes_in_graph = []
        self.graph.clear()
        self.atributos = {}

        for nombre, atributo in peliculas.items():
            nodo_name_for_graph = f"{nombre}\n {atributo['genero']}\n{atributo['director']}"
            
            self.nodes_in_graph.append(nodo_name_for_graph)
            self.graph.add_node(nodo_name_for_graph)
            self.atributos[nodo_name_for_graph] = atributo
            
    def crearAristas(self):
        # Use the instance variable for nodes
        for i in range(len(self.nodes_in_graph)):
            for j in range(i + 1, len(self.nodes_in_graph)):
                nodo1, nodo2 = self.nodes_in_graph[i], self.nodes_in_graph[j]
                atributo1, atributo2 = self.atributos[nodo1], self.atributos[nodo2]

                # Conexión por género
                if atributo1['genero'] == atributo2['genero']:
                    self.graph.add_edge(nodo1, nodo2)

                # Conexión por director
                elif atributo1['director'] == atributo2['director']:
                    self.graph.add_edge(nodo1, nodo2)

                # Conexion por estilo visual
                elif atributo1['estilo'] == atributo2['estilo']:
                    self.graph.add_edge(nodo1, nodo2)

    def bfs(self, inicio):
        visitados = set()
        cola = deque([inicio])
        recorrido = []

        if inicio not in self.graph.nodes:
            return [] # Return empty if start node not in graph

        while cola:
            nodo = cola.popleft()
            if nodo not in visitados:
                visitados.add(nodo)
                recorrido.append(nodo)
                # Use self.graph.successors for the instance graph
                vecinos = list(self.graph.successors(nodo))
                cola.extend([vecino for vecino in vecinos if vecino not in visitados])
        return recorrido
    
class Filmder:
    def __init__(self, parent_window): 
        self.parent_window = parent_window 
        self.g = Grafo()
        self.pelicula_data = self.g.leerJSON('peliculas.json')
        self.watchlist = []
        self.recorridoActual = []

        self.g.crearNodo(self.pelicula_data)
        self.g.crearAristas()
        
        self.ventana0 = None
        self.ventana = None
        self.elemento = None
        self.titulo = None
        self.sinopsis = None
        self.labelImagen = None
        self.botonVisto = None
        self.botonWatchlist = None
        self.botonNoInteresa = None

        self.ventanaIn() 

    def ventanaIn(self):
        if self.ventana0 and self.ventana0.winfo_exists():
            self.ventana0.deiconify() # Restore if minimized
            self.ventana0.lift() # Bring to front
            return

        self.ventana0 = tk.Toplevel(self.parent_window)
        self.ventana0.title('Filmder')
        self.ventana0.geometry('500x500+500+240')
        self.ventana0.withdraw() # Start hidden, will be shown by Programa

        menu_principal = tk.Menu(self.ventana0)
        menu_principal.add_command(label='Salir', command=self.ventana0.destroy)
        menu_principal.add_command(label='Watchlist', command=self.verWatchlist)
        self.ventana0.config(menu=menu_principal)

        tk.Label(self.ventana0, text='Escriba la pelicula que le gusto', font=('Arial',12)).grid(row=0, column=0, pady=10, padx=10)
        self.elemento = tk.Entry(self.ventana0, width=40)
        self.elemento.grid(row=1, column=0, pady=5, padx=10)
        
        self.botonA = tk.Button(self.ventana0, text='Buscar', command=self.buscar)
        self.botonA.grid(row=2, column=0, pady=10, padx=10)

        self.boton_mostrar_grafo = tk.Button(self.ventana0, text='Mostrar Grafo', command=self.mostrar_grafo)
        self.boton_mostrar_grafo.grid(row=3, column=0, pady=10, padx=10) # Adjust row as needed


    def ventanaPr(self, pelicula_node_string):
        if self.ventana and self.ventana.winfo_exists():
            self.ventana.destroy() # Destroy previous main window if open

        movie_title = pelicula_node_string.split('\n')[0].strip()

        self.atributos = self.g.atributos.get(pelicula_node_string)
        if not self.atributos:
            messagebox.showerror("Error", "No se encontraron atributos para la película seleccionada.")
            self.siguientePeli()
            return

        self.ventana = tk.Toplevel(self.parent_window) # Use Toplevel and pass parent_window
        self.ventana.title(f'Filmder - {movie_title}')
        self.ventana.geometry('700x500+500+240')
        self.ventana.transient(self.parent_window) # Make this window dependent on the main one

        menu_principal = tk.Menu(self.ventana)
        menu_principal.add_command(label='Salir', command=self.ventana.destroy)
        menu_principal.add_command(label='Watchlist', command=self.verWatchlist)
        self.ventana.config(menu=menu_principal)

        self.titulo = tk.Label(self.ventana, text=movie_title, font=('Arial', 16, 'bold'))
        self.titulo.grid(row=0, column=0, columnspan=3, pady=10)
        
        self.sinopsis = tk.Label(self.ventana, text="", wraplength=350, font=('Arial', 12), justify=tk.LEFT)
        self.sinopsis.grid(row=1, column=1, sticky="nw", padx=10)

        self.labelImagen = tk.Label(self.ventana)
        self.labelImagen.grid(row=1, column=0, pady=10, padx=20, sticky="n")

        self.botonVisto = tk.Button(self.ventana, text="Ya la vi", command=self.siguientePeli)
        self.botonVisto.grid(row=3, column=2, pady=10, padx=5)
        
        self.botonWatchlist = tk.Button(self.ventana, text="Añadir al Watchlist", command=self.listaPeliculas)
        self.botonWatchlist.grid(row=3, column=1, pady=10, padx=5)
        
        self.botonNoInteresa = tk.Button(self.ventana, text="No me interesa", command=self.siguientePeli)
        self.botonNoInteresa.grid(row=3, column=0, pady=10, padx=10)

        self.recomendacion(pelicula_node_string)

    def buscar(self):
        user_movie_input = self.elemento.get().strip()

        found_node_string = None
        for node_str in self.g.nodes_in_graph:
            if node_str.split('\n')[0].strip() == user_movie_input:
                found_node_string = node_str
                break
        
        if not found_node_string:
            messagebox.showwarning("Película no encontrada", f"La película '{user_movie_input}' no se encontró en nuestra base de datos. Por favor, intente con otra.")
            return

        self.recorrido = self.g.bfs(found_node_string)

        if len(self.recorrido) <= 1:
            messagebox.showinfo("No hay recomendaciones", "No se encontraron películas conectadas a la que buscaste.")
            return

        self.recorridoActual = self.recorrido[1:]
        
        if self.ventana0 and self.ventana0.winfo_exists():
            self.ventana0.withdraw() # Ocultar la ventana de búsqueda inicial
            # self.ventana0.destroy() # Or destroy it if you don't want to reuse
            # self.ventana0 = None

        self.ventanaPr(self.recorridoActual.pop(0))

    def siguientePeli(self):
        if self.recorridoActual:
            self.recomendacion(self.recorridoActual.pop(0))
        else:
            self.titulo.config(text="¡No hay más recomendaciones!", fg="red")
            self.sinopsis.config(text="Intenta buscar otra película o revisa tu Watchlist.")
            self.labelImagen.config(image='')
            self.labelImagen.image = None
            
            self.botonVisto.config(state=tk.DISABLED)
            self.botonWatchlist.config(state=tk.DISABLED)
            self.botonNoInteresa.config(state=tk.DISABLED)

    def recomendacion(self, pelicula_node_string):
        self.atributos = self.g.atributos.get(pelicula_node_string)
        if not self.atributos:
            messagebox.showerror("Error", "No se encontraron atributos para la película recomendada.")
            self.siguientePeli()
            return

        movie_title_for_display = pelicula_node_string.split('\n')[0].strip()
        self.titulo.config(text=movie_title_for_display)
        
        sinopsis_text = self.atributos.get('sinopsis', 'Sinopsis no disponible')
        if not sinopsis_text:
             sinopsis_text = 'Sinopsis no disponible'

        self.sinopsis.config(text=f"Género: {self.atributos.get('genero', 'N/A')}\n\n"
                                   f"{sinopsis_text}\n\n"
                                   f"Calificación en IMDB: {self.atributos.get('imdb', 'N/A')}")

        rutaImagen = self.atributos.get('imagen')
        if rutaImagen and isinstance(rutaImagen, str):
            try:
                imagen = Image.open(rutaImagen)
                imagen = imagen.resize((200, 300), Image.Resampling.LANCZOS)
                imagen_tk = ImageTk.PhotoImage(imagen)

                self.labelImagen.config(image=imagen_tk)
                self.labelImagen.image = imagen_tk
            except FileNotFoundError:
                messagebox.showwarning("Imagen no encontrada", f"No se encontró la imagen para: {movie_title_for_display}")
                self.labelImagen.config(image='')
                self.labelImagen.image = None
            except Exception as e:
                messagebox.showwarning("Error de Imagen", f"Error al cargar la imagen para {movie_title_for_display}: {e}")
                self.labelImagen.config(image='')
                self.labelImagen.image = None
        else:
            self.labelImagen.config(image='')
            self.labelImagen.image = None

    def listaPeliculas(self):
        peliActual_displayed_title = self.titulo.cget("text")
        
        # Find the full node string from the raw movie data using the displayed title
        peliActual_full_node_string = None
        for node_str in self.g.nodes_in_graph:
            if node_str.split('\n')[0].strip() == peliActual_displayed_title:
                peliActual_full_node_string = node_str
                break
        
        if peliActual_full_node_string and peliActual_full_node_string not in self.watchlist:
            self.watchlist.append(peliActual_full_node_string)
            messagebox.showinfo("Watchlist", f"'{peliActual_displayed_title}' añadido a tu Watchlist.")
        elif peliActual_full_node_string:
            messagebox.showinfo("Watchlist", f"'{peliActual_displayed_title}' ya está en tu Watchlist.")
        else:
            messagebox.showwarning("Error", "No se pudo añadir la película a la Watchlist.")

        self.siguientePeli()

    def verWatchlist(self):
        if not self.watchlist:
            messagebox.showinfo("Watchlist Vacía", "Tu Watchlist está vacía. ¡Añade algunas películas!")
            return

        watchlist_window = tk.Toplevel(self.parent_window) # Use parent_window
        watchlist_window.title("Mi Watchlist")
        watchlist_window.geometry("400x300")
        watchlist_window.transient(self.parent_window) # Make it modal to the main app window

        tk.Label(watchlist_window, text="Películas en tu Watchlist:", font=("Arial", 14, "bold")).pack(pady=10)

        watchlist_text = scrolledtext.ScrolledText(watchlist_window, width=45, height=10, wrap=tk.WORD, font=("Arial", 10))
        watchlist_text.pack(pady=5)

        for item in self.watchlist:
            display_name = item.split('\n')[0].strip() if '\n' in item else item
            watchlist_text.insert(tk.END, display_name + "\n")
        
        watchlist_text.config(state=tk.DISABLED)
        
    def mostrar_grafo(self):
        if not self.g.graph:
            messagebox.showinfo("Grafo Vacío", "No hay grafo para mostrar. Asegúrate de que las películas se hayan cargado correctamente.")
            return

        plt.figure(figsize=(15, 12)) # Tamaño de la figura ajustado

        # Define las posiciones de los nodos. Puedes probar diferentes layouts.
        pos = nx.spring_layout(self.g.graph, k=0.3, iterations=50) # Un buen layout para grafos

        # Listas para clasificar nodos y colores
        nodes_in_watchlist = [node for node in self.g.graph.nodes() if node in self.watchlist]
        nodes_not_in_watchlist = [node for node in self.g.graph.nodes() if node not in self.watchlist]

        # Dibujar nodos que NO están en la watchlist (color por defecto)
        nx.draw_networkx_nodes(self.g.graph, pos,
                               nodelist=nodes_not_in_watchlist,
                               node_size=3000,
                               node_color='lightblue',
                               alpha=0.8)

        # Dibujar nodos que SÍ están en la watchlist (color diferente, por ejemplo, rojo)
        nx.draw_networkx_nodes(self.g.graph, pos,
                               nodelist=nodes_in_watchlist,
                               node_size=3500, # Un poco más grandes para destacarlos
                               node_color='salmon', # Color rojo salmón para la watchlist
                               alpha=0.9,
                               edgecolors='black', # Borde negro para mayor distinción
                               linewidths=1.5)

        # Dibujar las aristas
        nx.draw_networkx_edges(self.g.graph, pos, edgelist=self.g.graph.edges(),
                               width=1, alpha=0.6, edge_color='gray', arrows=True)

        # Crear etiquetas de nodos (solo el título de la película)
        node_labels = {node: node.split('\n')[0].strip() for node in self.g.graph.nodes()}
        nx.draw_networkx_labels(self.g.graph, pos, labels=node_labels, font_size=8, font_weight='bold')

        plt.title("Grafo de Recomendación de Películas (Watchlist Resaltada)", size=18)
        plt.axis('off') # Ocultar los ejes
        plt.show()

# --- Variables globales para la pila y la cola ---
pila_data = [] # Cambiado de 'pila' para evitar conflicto con posibles funciones/clases
cola_data = []  # Cambiado de 'cola'

# --- Clase principal de la aplicación ---
class Programa:
    # --- Clase Nodo anidada dentro de Programa (ADAPTADA) ---
    class Nodo:
        def __init__(self, boleta, nombre, prom):
            self.boleta = boleta
            self.nombre = nombre
            self.prom = prom
            self.izq = None
            self.der = None

        def __str__(self):
            return f"Boleta: {self.boleta}, Nombre: {self.nombre}, Prom: {self.prom:.3f}"

    def __init__(self, master, tupla=(), lista=None, conjunto=None, diccionario=None):
        self.master = master
        master.title('Proyecto en Tkinter')
        master.geometry('600x400+55+35') # Ancho x Alto + Posición X + Posición Y

        # Contenedores
        self._tupla = ()
        self._lista = []
        self._conjunto = set()
        self._diccionario = {}
        
        # Pilas y colas
        self.ventana_pila_obj = None
        self.ventana_cola_obj = None

        # Nodos (Filmder)
        self.ventana_filmder_obj = None
        self.filmder_app = None

        # Contenedores 2
        self.ventana_tupla_obj = None
        self.ventana_lista_obj = None
        self.ventana_conjunto_obj = None
        self.ventana_diccionario_obj = None

        # Atributos para el ABB
        self._raiz_abb = None 
        self.ventana_abb_obj = None # Ventana Toplevel para el ABB
        
        # Atributos de UI para el ABB (se inicializan aquí para que existan)
        self.abb_boleta_entry = None
        self.abb_nombre_entry = None
        self.abb_parcial1_entry = None
        self.abb_parcial2_entry = None
        self.abb_parcial3_entry = None
        self.abb_mostrar_label = None # Para mostrar los recorridos
        self.abb_imagen_arbol_label = None # Para mostrar el grafo
        self.abb_busqueda_entry = None # Para la entrada de búsqueda/eliminación
        self.abb_boton_busqueda_aceptar = None # Botón aceptar para búsqueda/eliminación
        self.abb_label_busqueda_temp = None # Label temporal para búsqueda/eliminación

        # Datos iniciales para el ABB (transferidos de la clase ABB)
        self.personas_iniciales_abb = {
            'Caridad Medina':{'boleta':20252280, 'prom': 9.567},
            'Wes Anderson':{'boleta':20252023, 'prom':9.654},
            'Josh Dun':{'boleta':20254567, 'prom':7.478},
            'Luz Shelby':{'boleta':20251234, 'prom': 8.785},
            'Camilo Villaruel':{'boleta':20257890, 'prom': 7.987}
        }
        # Variable para almacenar el recorrido del árbol
        self.recorrido_abb = []

        # Inicializar el ABB con datos iniciales
        self._inicializar_abb_con_datos()

        # Atributos para Concurrencia (TRANSFERIDOS DE LA CLASE Concurrencia)
        self.ventana_concurrencia_obj = None
        self.cola_concurrencia = queue.Queue()
        self.lock_concurrencia = threading.Lock()
        self.atendidos_concurrencia = 0
        self.sem_concurrencia = None # Se inicializa en _atender_concurrencia
        self.cajas_progress_bars = {} # Diccionario para almacenar las barras de progreso por número de caja
        self.ventana_barras_concurrencia_obj = None # <--- Nueva ventana para las barras de progreso
        self.frame_barras = None # <--- Nuevo marco para contener las barras en la nueva ventana

        # Atributos de UI para Concurrencia
        self.concurrencia_cantidad_entry = None
        self.concurrencia_cajas_entry = None
        self.concurrencia_fila_text = None
        self.concurrencia_resultado_label = None


        # Atributos para los Entry y Text de la ventana de Contenedores
        self.entry_elemento = None
        self.display_tupla = None

        self.entry_lista_elemento = None
        self.display_lista = None

        self.entry_conjunto_elemento = None
        self.display_conjunto = None

        self.entry_diccionario_clave = None
        self.entry_diccionario_valor = None
        self.display_diccionario = None

        self._crear_menu()
        self.Portada()

    def _inicializar_abb_con_datos(self):
        for nombre, atributos in self.personas_iniciales_abb.items():
            boleta = atributos['boleta']
            prom = atributos['prom']
            if self._raiz_abb is None:
                self._raiz_abb = self.Nodo(boleta, nombre, prom)
            else:
                self._insertar_recursivo_abb(self._raiz_abb, boleta, nombre, prom)

    def _crear_menu(self):
        menu_principal = tk.Menu(self.master)
        self.master.config(menu=menu_principal)
        
        menu_1er_parcial = tk.Menu(menu_principal, tearoff=0)
        menu_1er_parcial.add_command(label="Tupla", command=self.mostrar_ventana_tupla)
        menu_1er_parcial.add_command(label="Lista", command=self.mostrar_ventana_lista)
        menu_1er_parcial.add_command(label="Conjunto", command=self.mostrar_ventana_conjunto)
        menu_1er_parcial.add_command(label="Diccionario", command=self.mostrar_ventana_diccionario)
        menu_1er_parcial.add_separator()
        menu_1er_parcial.add_command(label="Pila", command=self.mostrar_ventana_pila)
        menu_1er_parcial.add_command(label="Cola", command=self.mostrar_ventana_cola)
        menu_principal.add_cascade(label="1er Parcial", menu=menu_1er_parcial)

        menu_2do_parcial = tk.Menu(menu_principal, tearoff=0)
        menu_2do_parcial.add_command(label="Recomendador de Películas (Filmder)", command=self.mostrar_ventana_filmder)
        menu_2do_parcial.add_command(label="Mostrar Grafo Filmder", command=self._mostrar_grafo_filmder)
        menu_principal.add_cascade(label="2do Parcial", menu=menu_2do_parcial)

        menu_3er_parcial = tk.Menu(menu_principal, tearoff=0)
        menu_3er_parcial.add_command(label='Árbol Binario de Búsqueda (ABB)', command=self.mostrar_ventana_abb) 
        # Nueva opción para Concurrencia
        menu_3er_parcial.add_command(label='Simulación de Concurrencia', command=self.mostrar_ventana_concurrencia)
        menu_principal.add_cascade(label="3er Parcial", menu=menu_3er_parcial)
        
        menu_ayuda = tk.Menu(menu_principal, tearoff=0)
        menu_ayuda.add_command(label="Acerca de...", command=self.mostrar_acerca_de)
        menu_ayuda.add_separator()
        menu_ayuda.add_command(label="Cerrar Ventana Actual", command=self.cerrar_ventana_actual)
        menu_principal.add_cascade(label="Ayuda", menu=menu_ayuda)

    def Portada(self):
        # Contenido de la ventana principal
        tk.Label(self.master, text="Proyecto Final",
                 font=("Arial", 16)).pack(pady=50)
        tk.Label(self.master, text="Hecho por Nogueda Alcantara Gunther",
                 font=("Arial", 16)).pack(pady=10)
        tk.Label(self.master, text="2CV14",
                 font=("Arial", 16)).pack(pady=10)

    def add_to_tupla(self, elemento):
        self._tupla = self._tupla + (elemento,)

    def add_to_lista(self, elemento):
        self._lista.append(elemento)

    def add_to_conjunto(self, elemento):
        self._conjunto.add(elemento)

    def add_to_diccionario(self, clave, valor):
        self._diccionario[clave] = valor


    # --- Métodos generales de la aplicación ---
    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", "Este programa es para pasar el semestre.")
        
    def cerrar_ventana_actual(self):
        """Intenta cerrar la ventana de Pila, Cola o Contenedores si está abierta."""
        if self.ventana_tupla_obj and self.ventana_tupla_obj.winfo_exists():
            self.ventana_tupla_obj.destroy()
            self.ventana_tupla_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Tupla cerrada.")
        elif self.ventana_lista_obj and self.ventana_lista_obj.winfo_exists():
            self.ventana_lista_obj.destroy()
            self.ventana_lista_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Lista cerrada.")
        elif self.ventana_conjunto_obj and self.ventana_conjunto_obj.winfo_exists():
            self.ventana_conjunto_obj.destroy()
            self.ventana_conjunto_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Conjunto cerrada.")
        elif self.ventana_diccionario_obj and self.ventana_diccionario_obj.winfo_exists():
            self.ventana_diccionario_obj.destroy()
            self.ventana_diccionario_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Diccionario cerrada.")
        elif self.ventana_pila_obj and self.ventana_pila_obj.winfo_exists():
            self.ventana_pila_obj.destroy()
            self.ventana_pila_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Pila cerrada.")
        elif self.ventana_cola_obj and self.ventana_cola_obj.winfo_exists():
            self.ventana_cola_obj.destroy()
            self.ventana_cola_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Cola cerrada.")
        elif self.ventana_filmder_obj and self.ventana_filmder_obj.winfo_exists() and self.ventana_filmder_obj.state() == 'normal':
            self.ventana_filmder_obj.withdraw() # Ocultar
            messagebox.showinfo("Cerrar Ventana", "Ventana de Filmder oculta.")
        elif self.ventana_abb_obj and self.ventana_abb_obj.winfo_exists():
            self.ventana_abb_obj.destroy()
            self.ventana_abb_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana del ABB cerrada.")
        elif self.ventana_concurrencia_obj and self.ventana_concurrencia_obj.winfo_exists():
            self.ventana_concurrencia_obj.destroy()
            self.ventana_concurrencia_obj = None
            # También cierra la ventana de barras si está abierta
            if self.ventana_barras_concurrencia_obj and self.ventana_barras_concurrencia_obj.winfo_exists():
                self.ventana_barras_concurrencia_obj.destroy()
                self.ventana_barras_concurrencia_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Concurrencia cerrada.")
        elif self.ventana_barras_concurrencia_obj and self.ventana_barras_concurrencia_obj.winfo_exists():
            self.ventana_barras_concurrencia_obj.destroy()
            self.ventana_barras_concurrencia_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Barras de Concurrencia cerrada.")
        else:
            messagebox.showinfo("Cerrar Ventana", "No hay ventanas secundarias abiertas para cerrar.")
            
    def _convertir_elemento(self, s):
        """Intenta convertir un string a int o float, si es posible."""
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s

    def mostrar_ventana_tupla(self):
        if self.ventana_tupla_obj and self.ventana_tupla_obj.winfo_exists():
            self.ventana_tupla_obj.lift()
            return

        self.ventana_tupla_obj = tk.Toplevel(self.master)
        self.ventana_tupla_obj.title("Tupla")
        self.ventana_tupla_obj.geometry("400x300+200+150")

        tk.Label(self.ventana_tupla_obj, text="Añadir Elemento a Tupla:", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.ventana_tupla_obj, text="Elemento:").pack(pady=2)
        self.entry_tupla_elemento = tk.Entry(self.ventana_tupla_obj, width=30)
        self.entry_tupla_elemento.pack(pady=2)

        tk.Button(self.ventana_tupla_obj, text="Añadir a Tupla", command=self._anadir_tupla_ui).pack(pady=5)

        tk.Label(self.ventana_tupla_obj, text="Contenido de la Tupla:").pack(pady=5)
        self.display_tupla = scrolledtext.ScrolledText(self.ventana_tupla_obj, width=40, height=5, wrap=tk.WORD)
        self.display_tupla.pack(pady=5)
        # Call _actualizar_display_tupla AFTER self.display_tupla is packed
        self._actualizar_display_tupla()

    def _anadir_tupla_ui(self):
        elemento_str = self.entry_tupla_elemento.get().strip()
        if not elemento_str:
            messagebox.showwarning("Entrada Vacía", "Por favor, introduce un elemento.")
            return
        elemento = self._convertir_elemento(elemento_str)
        self.add_to_tupla(elemento)
        self._actualizar_display_tupla()
        self.entry_tupla_elemento.delete(0, tk.END)

    def _actualizar_display_tupla(self):
        if self.display_tupla and self.display_tupla.winfo_exists():
            self.display_tupla.config(state=tk.NORMAL)
            self.display_tupla.delete(1.0, tk.END)
            self.display_tupla.insert(tk.END, str(self._tupla))
            self.display_tupla.config(state=tk.DISABLED)

    # --- Methods for the List window ---
    def mostrar_ventana_lista(self):
        if self.ventana_lista_obj and self.ventana_lista_obj.winfo_exists():
            self.ventana_lista_obj.lift()
            return

        self.ventana_lista_obj = tk.Toplevel(self.master)
        self.ventana_lista_obj.title("Lista")
        self.ventana_lista_obj.geometry("400x300+250+200")

        tk.Label(self.ventana_lista_obj, text="Añadir Elemento a Lista:", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.ventana_lista_obj, text="Elemento:").pack(pady=2)
        self.entry_lista_elemento = tk.Entry(self.ventana_lista_obj, width=30)
        self.entry_lista_elemento.pack(pady=2)

        button_frame_lista = tk.Frame(self.ventana_lista_obj)
        button_frame_lista.pack(pady=5)

        tk.Button(self.ventana_lista_obj, text="Añadir a Lista", command=self._anadir_lista_ui).pack(pady=5)
        tk.Button(button_frame_lista, text="Eliminar de Lista", command=self._eliminar_lista_ui).pack(side=tk.LEFT, padx=5)

        tk.Label(self.ventana_lista_obj, text="Contenido de la Lista:").pack(pady=5)
        self.display_lista = scrolledtext.ScrolledText(self.ventana_lista_obj, width=40, height=5, wrap=tk.WORD)
        self.display_lista.pack(pady=5)
        # Call _actualizar_display_lista AFTER self.display_lista is packed
        self._actualizar_display_lista()

    def _anadir_lista_ui(self):
        elemento_str = self.entry_lista_elemento.get().strip()
        if not elemento_str:
            messagebox.showwarning("Entrada Vacía", "Por favor, introduce un elemento.")
            return
        elemento = self._convertir_elemento(elemento_str)
        self.add_to_lista(elemento)
        self._actualizar_display_lista()
        self.entry_lista_elemento.delete(0, tk.END)

    def _actualizar_display_lista(self):
        if self.display_lista and self.display_lista.winfo_exists():
            self.display_lista.config(state=tk.NORMAL)
            self.display_lista.delete(1.0, tk.END)
            self.display_lista.insert(tk.END, str(self._lista))
            self.display_lista.config(state=tk.DISABLED)

    def _eliminar_lista_ui(self):
        elemento_str = self.entry_lista_elemento.get().strip()
        if not elemento_str:
            messagebox.showwarning("Entrada Vacía", "Por favor, introduce el elemento a eliminar.")
            return
        elemento = self._convertir_elemento(elemento_str)
        if self.remove_from_lista(elemento):
            messagebox.showinfo("Éxito", f"'{elemento_str}' eliminado de la Lista.")
        else:
            messagebox.showwarning("Error", f"'{elemento_str}' no encontrado en la Lista.")
        self._actualizar_display_lista()
        self.entry_lista_elemento.delete(0, tk.END)

    def remove_from_lista(self, elemento):
        try:
            self._lista.remove(elemento)
            return True
        except ValueError:
            return False


    # --- Methods for the Set window ---
    def mostrar_ventana_conjunto(self):
        if self.ventana_conjunto_obj and self.ventana_conjunto_obj.winfo_exists():
            self.ventana_conjunto_obj.lift()
            return

        self.ventana_conjunto_obj = tk.Toplevel(self.master)
        self.ventana_conjunto_obj.title("Gestión de Conjunto")
        self.ventana_conjunto_obj.geometry("400x300+300+250")

        tk.Label(self.ventana_conjunto_obj, text="Añadir Elemento a Conjunto:", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.ventana_conjunto_obj, text="Elemento:").pack(pady=2)
        self.entry_conjunto_elemento = tk.Entry(self.ventana_conjunto_obj, width=30)
        self.entry_conjunto_elemento.pack(pady=2)

        button_frame_conjunto = tk.Frame(self.ventana_conjunto_obj)
        button_frame_conjunto.pack(pady=5)

        tk.Button(self.ventana_conjunto_obj, text="Añadir a Conjunto", command=self._anadir_conjunto_ui).pack(pady=5)
        tk.Button(button_frame_conjunto, text="Eliminar de Conjunto", command=self._eliminar_conjunto_ui).pack(side=tk.LEFT, padx=5)

        tk.Label(self.ventana_conjunto_obj, text="Contenido del Conjunto:").pack(pady=5)
        self.display_conjunto = scrolledtext.ScrolledText(self.ventana_conjunto_obj, width=40, height=5, wrap=tk.WORD)
        self.display_conjunto.pack(pady=5)
        # Call _actualizar_display_conjunto AFTER self.display_conjunto is packed
        self._actualizar_display_conjunto()

    def _anadir_conjunto_ui(self):
        elemento_str = self.entry_conjunto_elemento.get().strip()
        if not elemento_str:
            messagebox.showwarning("Entrada Vacía", "Por favor, introduce un elemento.")
            return
        elemento = self._convertir_elemento(elemento_str)
        self.add_to_conjunto(elemento)
        self._actualizar_display_conjunto()
        self.entry_conjunto_elemento.delete(0, tk.END)

    def _eliminar_conjunto_ui(self):
        elemento_str = self.entry_conjunto_elemento.get().strip()
        if not elemento_str:
            messagebox.showwarning("Entrada Vacía", "Por favor, introduce el elemento a eliminar.")
            return
        elemento = self._convertir_elemento(elemento_str)
        if self.remove_from_conjunto(elemento):
            messagebox.showinfo("Éxito", f"'{elemento_str}' eliminado del Conjunto.")
        else:
            messagebox.showwarning("Error", f"'{elemento_str}' no encontrado en el Conjunto.")
        self._actualizar_display_conjunto()
        self.entry_conjunto_elemento.delete(0, tk.END)

    def remove_from_conjunto(self, elemento):
        try:
            self._conjunto.remove(elemento)
            return True
        except KeyError:
            return False

    def _actualizar_display_conjunto(self):
        if self.display_conjunto and self.display_conjunto.winfo_exists():
            self.display_conjunto.config(state=tk.NORMAL)
            self.display_conjunto.delete(1.0, tk.END)
            self.display_conjunto.insert(tk.END, str(self._conjunto))
            self.display_conjunto.config(state=tk.DISABLED)

    # --- Methods for the Dictionary window ---
    def mostrar_ventana_diccionario(self):
        if self.ventana_diccionario_obj and self.ventana_diccionario_obj.winfo_exists():
            self.ventana_diccionario_obj.lift()
            return

        self.ventana_diccionario_obj = tk.Toplevel(self.master)
        self.ventana_diccionario_obj.title("Gestión de Diccionario")
        self.ventana_diccionario_obj.geometry("450x350+350+300")

        tk.Label(self.ventana_diccionario_obj, text="Añadir Elemento a Diccionario:", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.ventana_diccionario_obj, text="Clave:").pack(pady=2)
        self.entry_diccionario_clave = tk.Entry(self.ventana_diccionario_obj, width=30)
        self.entry_diccionario_clave.pack(pady=2)

        tk.Label(self.ventana_diccionario_obj, text="Valor:").pack(pady=2)
        self.entry_diccionario_valor = tk.Entry(self.ventana_diccionario_obj, width=30)
        self.entry_diccionario_valor.pack(pady=2)

        tk.Button(self.ventana_diccionario_obj, text="Añadir a Diccionario", command=self._anadir_diccionario_ui).pack(pady=5)

        tk.Label(self.ventana_diccionario_obj, text="Contenido del Diccionario:").pack(pady=5)
        self.display_diccionario = scrolledtext.ScrolledText(self.ventana_diccionario_obj, width=50, height=8, wrap=tk.WORD)
        self.display_diccionario.pack(pady=5)
        # Call _actualizar_display_diccionario AFTER self.display_diccionario is packed
        self._actualizar_display_diccionario()

    def _anadir_diccionario_ui(self):
        clave_str = self.entry_diccionario_clave.get().strip()
        valor_str = self.entry_diccionario_valor.get().strip()
        if not clave_str or not valor_str:
            messagebox.showwarning("Entrada Vacía", "Por favor, introduce clave y valor para el diccionario.")
            return

        clave = self._convertir_elemento(clave_str)
        valor = self._convertir_elemento(valor_str)

        self.add_to_diccionario(clave, valor)
        self._actualizar_display_diccionario()
        self.entry_diccionario_clave.delete(0, tk.END)
        self.entry_diccionario_valor.delete(0, tk.END)

    def _actualizar_display_diccionario(self):
        if self.display_diccionario and self.display_diccionario.winfo_exists():
            self.display_diccionario.config(state=tk.NORMAL)
            self.display_diccionario.delete(1.0, tk.END)
            self.display_diccionario.insert(tk.END, str(self._diccionario))
            self.display_diccionario.config(state=tk.DISABLED)

    def mostrar_ventana_pila(self):
        if self.ventana_pila_obj and self.ventana_pila_obj.winfo_exists():
            self.ventana_pila_obj.lift()
            return

        global entrada_nombre_pila, entrada_apellido_pila, etiqueta_pila_display
        self.ventana_pila_obj = tk.Toplevel(self.master)
        self.ventana_pila_obj.title("Pila")
        self.ventana_pila_obj.geometry("400x350+500+100") 

        tk.Label(self.ventana_pila_obj, text="Elementos de Pila (LIFO):", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.ventana_pila_obj, text="Nombre:", font=("Arial", 12)).pack(pady=2)
        entrada_nombre_pila = tk.Entry(self.ventana_pila_obj, width=30)
        entrada_nombre_pila.pack(pady=2)

        tk.Label(self.ventana_pila_obj, text="Apellido:", font=("Arial", 12)).pack(pady=2)
        entrada_apellido_pila = tk.Entry(self.ventana_pila_obj, width=30)
        entrada_apellido_pila.pack(pady=2)

        boton_frame = tk.Frame(self.ventana_pila_obj) 
        boton_frame.pack(pady=10)

        tk.Button(boton_frame, text="Agregar a Pila", command=self._agregar_pila_ui).pack(side=tk.LEFT, padx=5)
        tk.Button(boton_frame, text="Eliminar de Pila", command=self._eliminar_pila_ui).pack(side=tk.LEFT, padx=5)

        etiqueta_pila_display = tk.Label(self.ventana_pila_obj, text=f"Pila: {pila_data}", font=("Arial", 12))
        etiqueta_pila_display.pack(pady=10)


    def _agregar_pila_ui(self):
        nombre = entrada_nombre_pila.get().strip()
        apellido = entrada_apellido_pila.get().strip()
        if nombre and apellido:
            pila_data.append((nombre, apellido))
            etiqueta_pila_display.config(text=f"Pila: {pila_data}")
            entrada_nombre_pila.delete(0, tk.END)
            entrada_apellido_pila.delete(0, tk.END)
        else:
            messagebox.showwarning("Advertencia", "Todos los campos (Nombre y Apellido) son obligatorios para la Pila.")

    def _eliminar_pila_ui(self):
        if pila_data:
            nombre, apellido = pila_data.pop()
            etiqueta_pila_display.config(text=f"Pila: {pila_data}")
            messagebox.showinfo("Elemento Eliminado", f"Se eliminó de la Pila: Nombre: {nombre}, Apellido: {apellido}")
        else:
            messagebox.showwarning("Advertencia", "La pila está vacía. No hay elementos para eliminar.")

    def mostrar_ventana_cola(self):
        if self.ventana_cola_obj and self.ventana_cola_obj.winfo_exists():
            self.ventana_cola_obj.lift() 
            return

        global entrada_usuario_cola, entrada_operacion_cola, etiqueta_cola_display
        self.ventana_cola_obj = tk.Toplevel(self.master) # Se crea como ventana secundaria
        self.ventana_cola_obj.title("Gestión de Cola")
        self.ventana_cola_obj.geometry("400x350+950+100") # Posiciona la ventana

        tk.Label(self.ventana_cola_obj, text="Elementos de Cola (FIFO):", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.ventana_cola_obj, text="Usuario:", font=("Arial", 12)).pack(pady=2)
        entrada_usuario_cola = tk.Entry(self.ventana_cola_obj, width=30)
        entrada_usuario_cola.pack(pady=2)

        tk.Label(self.ventana_cola_obj, text="Operación:", font=("Arial", 12)).pack(pady=2)
        entrada_operacion_cola = tk.Entry(self.ventana_cola_obj, width=30)
        entrada_operacion_cola.pack(pady=2)

        boton_frame = tk.Frame(self.ventana_cola_obj) # Frame para agrupar botones
        boton_frame.pack(pady=10)

        tk.Button(boton_frame, text="Agregar a Cola", command=self._agregar_cola_ui).pack(side=tk.LEFT, padx=5)
        tk.Button(boton_frame, text="Eliminar de Cola", command=self._eliminar_cola_ui).pack(side=tk.LEFT, padx=5)

        etiqueta_cola_display = tk.Label(self.ventana_cola_obj, text=f"Cola: {cola_data}", font=("Arial", 12))
        etiqueta_cola_display.pack(pady=10)

    def _agregar_cola_ui(self):
        usuario = entrada_usuario_cola.get().strip()
        operacion = entrada_operacion_cola.get().strip()
        if usuario and operacion:
            cola_data.append((usuario, operacion))
            etiqueta_cola_display.config(text=f"Cola: {cola_data}")
            entrada_usuario_cola.delete(0, tk.END)
            entrada_operacion_cola.delete(0, tk.END)
        else:
            messagebox.showwarning("Advertencia", "Todos los campos (Usuario y Operación) son obligatorios para la Cola.")

    def _eliminar_cola_ui(self):
        if cola_data:
            usuario, operacion = cola_data.pop(0) # FIFO
            etiqueta_cola_display.config(text=f"Cola: {cola_data}")
            messagebox.showinfo("Elemento Eliminado", f"Se eliminó de la Cola: Usuario: {usuario}, Operación: {operacion}")
        else:
            messagebox.showwarning("Advertencia", "La cola está vacía. No hay elementos para eliminar.")

    # --- Métodos para Filmder ---
    def mostrar_ventana_filmder(self):
        """Muestra la ventana principal del recomendador de películas (Filmder)."""
        if self.ventana_filmder_obj and self.ventana_filmder_obj.winfo_exists():
            self.ventana_filmder_obj.lift() # Traer al frente si ya existe
            self.ventana_filmder_obj.deiconify() # Asegurarse de que esté visible si fue minimizada
            return

        # Crea la instancia de Filmder (si no existe) y pasa self.master como padre
        if not self.filmder_app:
            self.filmder_app = Filmder(self.master) # Pasar self.master para que Filmder sepa su padre
        
        # Reutilizar la ventana inicial de Filmder
        self.ventana_filmder_obj = self.filmder_app.ventana0
        self.ventana_filmder_obj.protocol("WM_DELETE_WINDOW", self._cerrar_ventana_filmder) # Capturar cierre de ventana
        self.ventana_filmder_obj.deiconify() # Asegurarse de que esté visible si fue minimizada

    def _cerrar_ventana_filmder(self):
        """Maneja el cierre de la ventana de Filmder."""
        if self.ventana_filmder_obj:
            self.ventana_filmder_obj.withdraw() # Ocultar en lugar de destruir para reutilizar
            messagebox.showinfo("Cerrar Ventana", "Ventana de Filmder oculta.")

    def _mostrar_grafo_filmder(self):
        """Llama al método para mostrar el grafo de Filmder."""
        if self.filmder_app:
            self.filmder_app.mostrar_grafo()
        else:
            messagebox.showwarning("Filmder no inicializado", "Por favor, abre la ventana de Filmder primero.")

    # --- Métodos para ABB ---
    def mostrar_ventana_abb(self):
        if self.ventana_abb_obj and self.ventana_abb_obj.winfo_exists():
            self.ventana_abb_obj.lift()
            return

        self.ventana_abb_obj = tk.Toplevel(self.master)
        self.ventana_abb_obj.title("Árbol Binario de Búsqueda (ABB)")
        self.ventana_abb_obj.geometry("700x600+100+100") # Tamaño y posición

        # Frame principal para organizar los widgets
        main_frame = ttk.Frame(self.ventana_abb_obj, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para entrada de datos
        input_frame = ttk.LabelFrame(main_frame, text="Gestión de Nodos", padding="10")
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Boleta:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.abb_boleta_entry = ttk.Entry(input_frame)
        self.abb_boleta_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="Nombre:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.abb_nombre_entry = ttk.Entry(input_frame)
        self.abb_nombre_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="Parcial 1:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.abb_parcial1_entry = ttk.Entry(input_frame)
        self.abb_parcial1_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="Parcial 2:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.abb_parcial2_entry = ttk.Entry(input_frame)
        self.abb_parcial2_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="Parcial 3:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.abb_parcial3_entry = ttk.Entry(input_frame)
        self.abb_parcial3_entry.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        input_frame.grid_columnconfigure(1, weight=1) # Permite que el Entry se expanda

        # Botones de acción
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Insertar", command=self._insertar_abb_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self._mostrar_dialogo_eliminar_abb).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Buscar", command=self._mostrar_dialogo_buscar_abb).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ver Árbol", command=self._ver_arbol_abb).pack(side=tk.LEFT, padx=5)

        # Frame para mostrar resultados de recorridos
        output_frame = ttk.LabelFrame(main_frame, text="Recorridos y Búsqueda", padding="10")
        output_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.abb_mostrar_label = ttk.Label(output_frame, text="Recorridos aquí...", wraplength=400, justify=tk.LEFT)
        self.abb_mostrar_label.pack(fill=tk.BOTH, expand=True)

        # Botones de recorrido
        recorrido_button_frame = ttk.Frame(output_frame)
        recorrido_button_frame.pack(pady=5)
        ttk.Button(recorrido_button_frame, text="Inorden", command=self._inorden_abb_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(recorrido_button_frame, text="Preorden", command=self._preorden_abb_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(recorrido_button_frame, text="Postorden", command=self._postorden_abb_ui).pack(side=tk.LEFT, padx=5)

        # Área para la imagen del árbol
        image_frame = ttk.LabelFrame(main_frame, text="Visualización del Árbol", padding="10")
        image_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew") # Ocupa 2 filas
        main_frame.grid_columnconfigure(1, weight=1) # Columna de la imagen expandible
        main_frame.grid_rowconfigure(0, weight=1) # Las filas de input y output también se expanden
        main_frame.grid_rowconfigure(1, weight=1)

        self.abb_imagen_arbol_label = ttk.Label(image_frame)
        self.abb_imagen_arbol_label.pack(fill=tk.BOTH, expand=True)

        self._ver_arbol_abb() # Mostrar el árbol inicial al abrir la ventana

    def _insertar_abb_ui(self):
        try:
            boleta = int(self.abb_boleta_entry.get())
            nombre = self.abb_nombre_entry.get().strip()
            p1 = float(self.abb_parcial1_entry.get())
            p2 = float(self.abb_parcial2_entry.get())
            p3 = float(self.abb_parcial3_entry.get())

            if not nombre:
                messagebox.showwarning("Entrada Inválida", "El nombre no puede estar vacío.")
                return
            if not (0 <= p1 <= 10 and 0 <= p2 <= 10 and 0 <= p3 <= 10):
                messagebox.showwarning("Entrada Inválida", "Las calificaciones deben estar entre 0 y 10.")
                return

            prom = (p1 + p2 + p3) / 3

            if self._raiz_abb is None:
                self._raiz_abb = self.Nodo(boleta, nombre, prom)
                messagebox.showinfo("Éxito", f"Nodo raíz insertado: {nombre} ({boleta})")
            else:
                if self._insertar_recursivo_abb(self._raiz_abb, boleta, nombre, prom):
                    messagebox.showinfo("Éxito", f"Nodo insertado: {nombre} ({boleta})")
                else:
                    messagebox.showwarning("Advertencia", f"La boleta {boleta} ya existe en el árbol.")
            
            self._limpiar_entradas_abb()
            self._ver_arbol_abb() # Actualizar visualización del árbol
        except ValueError:
            messagebox.showerror("Error de Entrada", "Asegúrate de que la boleta y las calificaciones sean números válidos.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al insertar: {e}")

    def _insertar_recursivo_abb(self, nodo, boleta, nombre, prom):
        if boleta < nodo.boleta:
            if nodo.izq is None:
                nodo.izq = self.Nodo(boleta, nombre, prom)
                return True
            else:
                return self._insertar_recursivo_abb(nodo.izq, boleta, nombre, prom)
        elif boleta > nodo.boleta:
            if nodo.der is None:
                nodo.der = self.Nodo(boleta, nombre, prom)
                return True
            else:
                return self._insertar_recursivo_abb(nodo.der, boleta, nombre, prom)
        else:
            return False # La boleta ya existe

    def _mostrar_dialogo_eliminar_abb(self):
        self._mostrar_dialogo_accion_abb("Eliminar", self._eliminar_abb_ui)

    def _eliminar_abb_ui(self, boleta_str):
        try:
            boleta = int(boleta_str)
            self._raiz_abb = self._eliminar_recursivo_abb(self._raiz_abb, boleta)
            if self.recorrido_abb: # Si se encontró y eliminó
                messagebox.showinfo("Éxito", f"Nodo con boleta {boleta} eliminado.")
                self._ver_arbol_abb()
            else:
                messagebox.showwarning("No Encontrado", f"Nodo con boleta {boleta} no encontrado.")
            self._limpiar_dialogo_accion_abb() # Limpiar el diálogo de búsqueda/eliminación
        except ValueError:
            messagebox.showerror("Error de Entrada", "La boleta debe ser un número entero.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al eliminar: {e}")

    def _eliminar_recursivo_abb(self, nodo, boleta):
        if nodo is None:
            self.recorrido_abb = [] # Indicar que no se encontró
            return None
        
        if boleta < nodo.boleta:
            nodo.izq = self._eliminar_recursivo_abb(nodo.izq, boleta)
        elif boleta > nodo.boleta:
            nodo.der = self._eliminar_recursivo_abb(nodo.der, boleta)
        else: # ¡Nodo encontrado!
            self.recorrido_abb = [f"Eliminando {nodo.nombre} ({nodo.boleta})"] # Marcar que se encontró
            # Caso 1: Nodo sin hijos o con un solo hijo
            if nodo.izq is None:
                return nodo.der
            elif nodo.der is None:
                return nodo.izq
            # Caso 2: Nodo con dos hijos
            else:
                temp = self._encontrar_minimo_abb(nodo.der)
                nodo.boleta = temp.boleta
                nodo.nombre = temp.nombre
                nodo.prom = temp.prom
                nodo.der = self._eliminar_recursivo_abb(nodo.der, temp.boleta)
        return nodo

    def _encontrar_minimo_abb(self, nodo):
        current = nodo
        while current.izq is not None:
            current = current.izq
        return current

    def _mostrar_dialogo_buscar_abb(self):
        self._mostrar_dialogo_accion_abb("Buscar", self._buscar_abb_ui)

    def _buscar_abb_ui(self, boleta_str):
        try:
            boleta = int(boleta_str)
            encontrado = self._buscar_recursivo_abb(self._raiz_abb, boleta)
            if encontrado:
                self.abb_label_busqueda_temp.config(text=f"Encontrado: {encontrado.nombre} (Boleta: {encontrado.boleta}, Prom: {encontrado.prom:.3f})", fg="blue")
            else:
                self.abb_label_busqueda_temp.config(text=f"Boleta {boleta} no encontrada.", fg="red")
            self._actualizar_recorrido_display()
        except ValueError:
            self.abb_label_busqueda_temp.config(text="La boleta debe ser un número entero.", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al buscar: {e}")

    def _buscar_recursivo_abb(self, nodo, boleta):
        self.recorrido_abb = [] # Limpiar recorrido
        while nodo is not None:
            self.recorrido_abb.append(f"Visitando: {nodo.nombre} ({nodo.boleta})")
            if boleta == nodo.boleta:
                return nodo
            elif boleta < nodo.boleta:
                nodo = nodo.izq
            else:
                nodo = nodo.der
        return None
    
    def _mostrar_dialogo_accion_abb(self, accion, command_func):
        # Destruir el diálogo anterior si existe
        if self.abb_boton_busqueda_aceptar and self.abb_boton_busqueda_aceptar.winfo_exists():
            self.abb_boton_busqueda_aceptar.master.destroy()

        dialog = tk.Toplevel(self.ventana_abb_obj)
        dialog.title(f"{accion} Nodo por Boleta")
        dialog.geometry("300x150")
        dialog.transient(self.ventana_abb_obj) # Hace que dependa de la ventana del ABB
        dialog.grab_set() # Bloquea interacción con otras ventanas hasta que se cierre

        tk.Label(dialog, text=f"Introduce la boleta a {accion.lower()}:").pack(pady=10)
        self.abb_busqueda_entry = tk.Entry(dialog)
        self.abb_busqueda_entry.pack(pady=5)

        self.abb_boton_busqueda_aceptar = tk.Button(dialog, text="Aceptar", command=lambda: command_func(self.abb_busqueda_entry.get()))
        self.abb_boton_busqueda_aceptar.pack(pady=10)

        self.abb_label_busqueda_temp = tk.Label(dialog, text="") # Para mensajes temporales
        self.abb_label_busqueda_temp.pack(pady=5)

    def _limpiar_dialogo_accion_abb(self):
        if self.abb_boton_busqueda_aceptar and self.abb_boton_busqueda_aceptar.winfo_exists():
            self.abb_boton_busqueda_aceptar.master.destroy() # Destruir la ventana Toplevel del diálogo
        self.abb_busqueda_entry = None
        self.abb_boton_busqueda_aceptar = None
        self.abb_label_busqueda_temp = None
        self.recorrido_abb = [] # Limpiar el recorrido después de una operación
        self._actualizar_recorrido_display()

    def _ver_arbol_abb(self):
        if not self._raiz_abb:
            self.abb_imagen_arbol_label.config(image='')
            self.abb_imagen_arbol_label.image = None
            self.abb_mostrar_label.config(text="El árbol está vacío.")
            return

        dot = Digraph(comment='Árbol Binario de Búsqueda')
        dot.attr(rankdir='TB') # Top to Bottom

        def add_nodes_edges(node):
            if node:
                dot.node(str(node.boleta), f"{node.nombre}\n({node.boleta})\nProm:{node.prom:.3f}")
                if node.izq:
                    dot.edge(str(node.boleta), str(node.izq.boleta))
                    add_nodes_edges(node.izq)
                if node.der:
                    dot.edge(str(node.boleta), str(node.der.boleta))
                    add_nodes_edges(node.der)

        add_nodes_edges(self._raiz_abb)

        try:
            # Renderizar a formato PNG directamente en memoria
            img_data = dot.pipe(format='png')
            image = Image.open(io.BytesIO(img_data))
            # Escalar la imagen para que quepa en el label
            max_width = self.abb_imagen_arbol_label.winfo_width() if self.abb_imagen_arbol_label.winfo_width() > 0 else 500
            max_height = self.abb_imagen_arbol_label.winfo_height() if self.abb_imagen_arbol_label.winfo_height() > 0 else 400
            
            # Mantener la relación de aspecto
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.abb_imagen_arbol_label.config(image=photo)
            self.abb_imagen_arbol_label.image = photo # Evitar que la imagen sea recolectada por el GC
        except Exception as e:
            messagebox.showerror("Error al graficar", f"Asegúrate de que Graphviz esté instalado y en tu PATH.\nError: {e}")
            self.abb_imagen_arbol_label.config(image='')
            self.abb_imagen_arbol_label.image = None

    def _inorden_abb_ui(self):
        self.recorrido_abb = [] # Limpiar antes de un nuevo recorrido
        self._inorden_recursivo_abb(self._raiz_abb)
        self._actualizar_recorrido_display()

    def _inorden_recursivo_abb(self, nodo):
        if nodo:
            self._inorden_recursivo_abb(nodo.izq)
            self.recorrido_abb.append(f"{nodo.nombre} ({nodo.boleta})")
            self._inorden_recursivo_abb(nodo.der)

    def _preorden_abb_ui(self):
        self.recorrido_abb = []
        self._preorden_recursivo_abb(self._raiz_abb)
        self._actualizar_recorrido_display()

    def _preorden_recursivo_abb(self, nodo):
        if nodo:
            self.recorrido_abb.append(f"{nodo.nombre} ({nodo.boleta})")
            self._preorden_recursivo_abb(nodo.izq)
            self._preorden_recursivo_abb(nodo.der)

    def _postorden_abb_ui(self):
        self.recorrido_abb = []
        self._postorden_recursivo_abb(self._raiz_abb)
        self._actualizar_recorrido_display()

    def _postorden_recursivo_abb(self, nodo):
        if nodo:
            self._postorden_recursivo_abb(nodo.izq)
            self._postorden_recursivo_abb(nodo.der)
            self.recorrido_abb.append(f"{nodo.nombre} ({nodo.boleta})")

    def _actualizar_recorrido_display(self):
        if self.abb_mostrar_label:
            if not self.recorrido_abb:
                self.abb_mostrar_label.config(text="El árbol está vacío o no hay recorrido para mostrar.")
            else:
                self.abb_mostrar_label.config(text="Recorrido: " + ", ".join(self.recorrido_abb))
            self.recorrido_abb = [] # Limpiar después de mostrar

    def _limpiar_entradas_abb(self):
        self.abb_boleta_entry.delete(0, tk.END)
        self.abb_nombre_entry.delete(0, tk.END)
        self.abb_parcial1_entry.delete(0, tk.END)
        self.abb_parcial2_entry.delete(0, tk.END)
        self.abb_parcial3_entry.delete(0, tk.END)
        self.abb_boleta_entry.focus_set() # Pone el foco en el primer campo

    # --- Métodos para Concurrencia ---
    def mostrar_ventana_concurrencia(self):
        if self.ventana_concurrencia_obj and self.ventana_concurrencia_obj.winfo_exists():
            self.ventana_concurrencia_obj.lift()
            return

        self.ventana_concurrencia_obj = tk.Toplevel(self.master)
        self.ventana_concurrencia_obj.title("Simulación de Concurrencia")
        self.ventana_concurrencia_obj.geometry("500x550+100+100") # Posición para no solapar la nueva ventana de barras

        tk.Label(self.ventana_concurrencia_obj, text="Simulación de Atención al Cliente", font=("Arial", 14, "bold")).pack(pady=10)

        # Controles de entrada
        input_frame = ttk.Frame(self.ventana_concurrencia_obj)
        input_frame.pack(pady=5)

        ttk.Label(input_frame, text="Cantidad de clientes:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.concurrencia_cantidad_entry = ttk.Entry(input_frame, width=10)
        self.concurrencia_cantidad_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        self.concurrencia_cantidad_entry.insert(0, "10") # Valor por defecto

        ttk.Label(input_frame, text="Número de cajas:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.concurrencia_cajas_entry = ttk.Entry(input_frame, width=10)
        self.concurrencia_cajas_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        self.concurrencia_cajas_entry.insert(0, "3") # Valor por defecto

        ttk.Button(input_frame, text="Iniciar Simulación", command=self._atender_concurrencia).grid(row=2, column=0, columnspan=2, pady=10)

        # Área de mensajes de la fila (ScrolledText)
        tk.Label(self.ventana_concurrencia_obj, text="Actividad de la Fila:").pack(pady=5)
        self.concurrencia_fila_text = scrolledtext.ScrolledText(self.ventana_concurrencia_obj, width=60, height=15, wrap=tk.WORD)
        self.concurrencia_fila_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.concurrencia_fila_text.config(state=tk.DISABLED) # Solo lectura

        self.concurrencia_resultado_label = tk.Label(self.ventana_concurrencia_obj, text="Clientes atendidos: 0", font=("Arial", 12, "bold"))
        self.concurrencia_resultado_label.pack(pady=10)

    def _cerrar_ventana_barras_concurrencia(self):
        """Maneja el cierre de la ventana de barras de progreso."""
        if self.ventana_barras_concurrencia_obj:
            self.ventana_barras_concurrencia_obj.destroy()
            self.ventana_barras_concurrencia_obj = None
            messagebox.showinfo("Simulación", "Ventana de estado de cajas cerrada. La simulación puede continuar en segundo plano hasta que se atiendan todos los clientes o se cierre la ventana principal de concurrencia.")
            
    def _atender_concurrencia(self):
        try:
            num_clientes = int(self.concurrencia_cantidad_entry.get())
            num_cajas = int(self.concurrencia_cajas_entry.get())
        except ValueError:
            messagebox.showerror("Entrada inválida", "Por favor, introduce números enteros para clientes y cajas.")
            return

        if num_clientes <= 0 or num_cajas <= 0:
            messagebox.showwarning("Entrada inválida", "La cantidad de clientes y el número de cajas deben ser mayores que cero.")
            return

        # --- Configuración de la nueva ventana para barras de progreso ---
        if self.ventana_barras_concurrencia_obj and self.ventana_barras_concurrencia_obj.winfo_exists():
            self.ventana_barras_concurrencia_obj.destroy() # Cierra la anterior si está abierta

        self.ventana_barras_concurrencia_obj = tk.Toplevel(self.master)
        self.ventana_barras_concurrencia_obj.title("Estado de Cajas")
        # Posicionar esta ventana al lado de la principal de concurrencia
        # Obtener la geometría de la ventana principal de concurrencia
        self.ventana_concurrencia_obj.update_idletasks() # Asegurarse de que la geometría esté actualizada
        x = self.ventana_concurrencia_obj.winfo_x()
        y = self.ventana_concurrencia_obj.winfo_y()
        width = self.ventana_concurrencia_obj.winfo_width()
        self.ventana_barras_concurrencia_obj.geometry(f"300x{self.ventana_concurrencia_obj.winfo_height()}+{x + width + 20}+{y}") # 20px de margen

        # Protocolo para manejar el cierre de la ventana de barras
        self.ventana_barras_concurrencia_obj.protocol("WM_DELETE_WINDOW", self._cerrar_ventana_barras_concurrencia)

        self.frame_barras = ttk.Frame(self.ventana_barras_concurrencia_obj, padding="10")
        self.frame_barras.pack(fill='both', expand=True)

        tk.Label(self.frame_barras, text="Progreso de Cajas:", font=("Arial", 12, "bold")).pack(pady=5)
        # --- Fin de Configuración de la nueva ventana ---

        # Limpiar cola y contadores
        while not self.cola_concurrencia.empty():
            self.cola_concurrencia.get()
        self.atendidos_concurrencia = 0
        self.concurrencia_resultado_label.config(text="Clientes atendidos: 0")
        self.concurrencia_fila_text.config(state=tk.NORMAL)
        self.concurrencia_fila_text.delete(1.0, tk.END)
        self.concurrencia_fila_text.config(state=tk.DISABLED)

        # Llenar la cola con clientes
        for i in range(num_clientes):
            self.cola_concurrencia.put(f'Cliente {i+1}')
        
        self.sem_concurrencia = threading.Semaphore(num_cajas)

        # Limpiar y crear barras de progreso
        # Clear existing progress bars and labels within the new frame
        for widget in self.frame_barras.winfo_children():
            if widget != self.frame_barras.winfo_children()[0]: # Keep the title label
                widget.destroy() 

        self.cajas_progress_bars = {} # Re-initialize the dictionary here to ensure it's clean for a new run

        # Create progress bars for each 'caja' in the new frame
        for i in range(num_cajas):
            label_caja = tk.Label(self.frame_barras, text=f'Caja {i+1}:')
            label_caja.pack(pady=(5, 0), anchor='w') # Use pack for vertical arrangement

            pbar = ttk.Progressbar(self.frame_barras, orient='horizontal', length=250, mode='determinate')
            pbar.pack(pady=(0, 10), fill='x')
            pbar['value'] = 0

            self.cajas_progress_bars[i] = {'label': label_caja, 'bar': pbar}
        
        # Start threads for each 'caja'
        hilos_cajas = []
        for i in range(num_cajas):
            hilo = threading.Thread(target=self._caja_concurrencia, args=(i,))
            hilos_cajas.append(hilo)
            hilo.start()

        # Monitor thread to wait for all clients to be attended
        monitor_hilo = threading.Thread(target=self._monitorear_concurrencia, args=(num_clientes, hilos_cajas))
        monitor_hilo.start()

    def _insertar_texto_concurrencia(self, texto):
        self.concurrencia_fila_text.config(state=tk.NORMAL)
        self.concurrencia_fila_text.insert(tk.END, texto + "\n")
        self.concurrencia_fila_text.see(tk.END) # Scroll to the end
        self.concurrencia_fila_text.config(state=tk.DISABLED)

    def _caja_concurrencia(self, numero):
        # Retrieve progress_bar directly from the dictionary
        progress_bar = self.cajas_progress_bars.get(numero, {}).get('bar')
        if not progress_bar: # Safety check
            # This error print is helpful for debugging if bars don't show up.
            # In a final app, you might remove it or log it silently.
            print(f"Error: No se encontró la barra de progreso para la caja {numero}") 
            return 

        # Reset progress bar to 0 at the start of a new client
        if self.ventana_concurrencia_obj.winfo_exists(): # Check if main window is still open
            self.ventana_concurrencia_obj.after(0, progress_bar.configure, {'value': 0})
            self.ventana_concurrencia_obj.after(0, progress_bar.start, 10) # Start animation

        while True:
            try:
                cliente = self.cola_concurrencia.get(timeout=2) # Wait for 2 seconds for a client
            except queue.Empty:
                # No more clients in the queue, this caja can stop
                if self.ventana_concurrencia_obj.winfo_exists():
                    self.ventana_concurrencia_obj.after(0, self._insertar_texto_concurrencia, f'[Caja--{numero+1}] No hay más clientes. Cerrando caja.')
                    self.ventana_concurrencia_obj.after(0, progress_bar.configure, {'value': 0}) # Reset bar when done
                    self.ventana_concurrencia_obj.after(0, progress_bar.stop)
                break

            with self.sem_concurrencia:
                if self.ventana_concurrencia_obj.winfo_exists():
                    self.ventana_concurrencia_obj.after(0, self._insertar_texto_concurrencia, f'[Caja--{numero+1}] Atendiendo a {cliente}')
                
                atencion_tiempo = random.uniform(0.2, 0.6) # Tiempo de atención entre 0.2 y 0.6 segundos
                intervalos = 20
                tiempo_por_intervalo = atencion_tiempo / intervalos

                for i in range(intervalos + 1):
                    time.sleep(tiempo_por_intervalo)
                    progress = int((i / intervalos) * 100)
                    if self.ventana_concurrencia_obj.winfo_exists():
                        self.ventana_concurrencia_obj.after(0, progress_bar.configure, {'value': progress})
                    
                if self.ventana_concurrencia_obj.winfo_exists():
                    self.ventana_concurrencia_obj.after(0, progress_bar.configure, {'value': 100}) # Ensure it ends at 100
                    self.ventana_concurrencia_obj.after(0, progress_bar.stop)
                    self.ventana_concurrencia_obj.after(0, self._insertar_texto_concurrencia, f'[Caja--{numero+1}] Terminó de atender a {cliente}.')
                
                # Incrementar el contador de atendidos de forma segura
                with self.lock_concurrencia:
                    self.atendidos_concurrencia += 1
                    if self.ventana_concurrencia_obj.winfo_exists():
                        self.ventana_concurrencia_obj.after(0, self.concurrencia_resultado_label.config, {'text': f"Clientes atendidos: {self.atendidos_concurrencia}"})
                
                self.cola_concurrencia.task_done() # Señalar que una tarea de la cola ha sido completada
    
    def _monitorear_concurrencia(self, num_clientes, hilos_cajas):
        # Esperar a que todos los clientes sean procesados por la cola
        self.cola_concurrencia.join() # Bloquea hasta que todos los items de la cola sean procesados

        # Esperar a que todos los hilos de caja terminen
        for hilo in hilos_cajas:
            hilo.join()
        
        if self.ventana_concurrencia_obj.winfo_exists():
            self.ventana_concurrencia_obj.after(0, self._insertar_texto_concurrencia, "\n--- Simulación Terminada ---")
            self.ventana_concurrencia_obj.after(0, self._insertar_texto_concurrencia, f"Total de clientes atendidos: {self.atendidos_concurrencia}")
            messagebox.showinfo("Simulación Terminada", f"Se han atendido todos los {num_clientes} clientes.")
            
            # Cierra la ventana de barras automáticamente al finalizar la simulación
            if self.ventana_barras_concurrencia_obj and self.ventana_barras_concurrencia_obj.winfo_exists():
                self.ventana_barras_concurrencia_obj.destroy()
                self.ventana_barras_concurrencia_obj = None


# --- Función Principal ---
if __name__ == '__main__':
    root = tk.Tk()
    mi_app = Programa(root)
    root.mainloop()
