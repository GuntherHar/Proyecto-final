import tkinter as tk
from tkinter import messagebox, scrolledtext

# --- Global variables for stack and queue (outside classes) ---
pila_data = []
cola_data = []

# --- Programa Class: Manages all UI and data logic ---
class Programa:
    def __init__(self, master):
        self.master = master
        master.title('Aplicación con Menús y Estructuras de Datos')
        master.geometry('700x500+55+35')

        # --- Containers (now managed individually or in their own windows) ---
        self._tupla = ()
        self._lista = []
        self._conjunto = set()
        self._diccionario = {}

        # Attributes for secondary windows (Toplevel)
        self.ventana_pila_obj = None
        self.ventana_cola_obj = None
        self.ventana_tupla_obj = None
        self.ventana_lista_obj = None
        self.ventana_conjunto_obj = None
        self.ventana_diccionario_obj = None

        # Attributes for Entry and Text widgets of individual windows
        self.entry_tupla_elemento = None
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

    def _crear_menu(self):
        menu_principal = tk.Menu(self.master)
        self.master.config(menu=menu_principal)

        # Submenu "1er Parcial"
        menu_1er_parcial = tk.Menu(menu_principal, tearoff=0)
        menu_1er_parcial.add_command(label="Pila", command=self.mostrar_ventana_pila)
        menu_1er_parcial.add_command(label="Cola", command=self.mostrar_ventana_cola)
        menu_1er_parcial.add_separator()

        menu_1er_parcial.add_command(label="Tupla", command=self.mostrar_ventana_tupla)
        menu_1er_parcial.add_command(label="Lista", command=self.mostrar_ventana_lista)
        menu_1er_parcial.add_command(label="Conjunto", command=self.mostrar_ventana_conjunto)
        menu_1er_parcial.add_command(label="Diccionario", command=self.mostrar_ventana_diccionario)

        menu_principal.add_cascade(label="1er Parcial", menu=menu_1er_parcial)

        # Submenu "2do Parcial" (empty for now)
        menu_2do_parcial = tk.Menu(menu_principal, tearoff=0)
        menu_principal.add_cascade(label="2do Parcial", menu=menu_2do_parcial)

        # Submenu "3er Parcial" (empty for now)
        menu_3er_parcial = tk.Menu(menu_principal, tearoff=0)
        menu_principal.add_cascade(label="3er Parcial", menu=menu_3er_parcial)

        # Submenu "Archivo"
        menu_archivo = tk.Menu(menu_principal, tearoff=0)
        menu_archivo.add_command(label="Cerrar Ventana Actual", command=self.cerrar_ventana_actual)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.salir_aplicacion)
        menu_principal.add_cascade(label="Archivo", menu=menu_archivo)

        # Submenu "Ayuda"
        menu_ayuda = tk.Menu(menu_principal, tearoff=0)
        menu_ayuda.add_command(label="Acerca de...", command=self.mostrar_acerca_de)
        menu_principal.add_cascade(label="Ayuda", menu=menu_ayuda)

    def Portada(self):
        for widget in self.master.winfo_children():
            if isinstance(widget, (tk.Label, tk.Frame)):
                widget.destroy()

        tk.Label(self.master, text="Proyecto Final",
                 font=("Arial", 20, "bold")).pack(pady=50)
        tk.Label(self.master, text="Hecho por Nogueda Alcantara Gunther",
                 font=("Arial", 14)).pack(pady=10)
        tk.Label(self.master, text="2CV14",
                 font=("Arial", 12)).pack(pady=10)
        tk.Label(self.master, text="Usa el menú superior para acceder a las funcionalidades.",
                 font=("Arial", 10, "italic")).pack(pady=20)

    # --- Container management methods (operate on self attributes) ---
    def add_to_tupla(self, elemento):
        self._tupla = self._tupla + (elemento,)

    def add_to_lista(self, elemento):
        self._lista.append(elemento)

    def add_to_conjunto(self, elemento):
        self._conjunto.add(elemento)

    def add_to_diccionario(self, clave, valor):
        self._diccionario[clave] = valor

    # --- General application methods ---
    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", "Este programa es para pasar el semestre.")

    def salir_aplicacion(self):
        self.master.quit()

    def cerrar_ventana_actual(self):
        if self.ventana_pila_obj and self.ventana_pila_obj.winfo_exists():
            self.ventana_pila_obj.destroy()
            self.ventana_pila_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Pila cerrada.")
        elif self.ventana_cola_obj and self.ventana_cola_obj.winfo_exists():
            self.ventana_cola_obj.destroy()
            self.ventana_cola_obj = None
            messagebox.showinfo("Cerrar Ventana", "Ventana de Cola cerrada.")
        elif self.ventana_tupla_obj and self.ventana_tupla_obj.winfo_exists():
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
        else:
            messagebox.showinfo("Cerrar Ventana", "No hay ventanas secundarias abiertas para cerrar.")

    # --- Methods for the Stack window ---
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
        global entrada_nombre_pila, entrada_apellido_pila, etiqueta_pila_display
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
        global etiqueta_pila_display
        if pila_data:
            nombre, apellido = pila_data.pop()
            etiqueta_pila_display.config(text=f"Pila: {pila_data}")
            messagebox.showinfo("Elemento Eliminado", f"Se eliminó de la Pila: Nombre: {nombre}, Apellido: {apellido}")
        else:
            messagebox.showwarning("Advertencia", "La pila está vacía. No hay elementos para eliminar.")

    # --- Methods for the Queue window ---
    def mostrar_ventana_cola(self):
        if self.ventana_cola_obj and self.ventana_cola_obj.winfo_exists():
            self.ventana_cola_obj.lift()
            return

        global entrada_usuario_cola, entrada_operacion_cola, etiqueta_cola_display
        self.ventana_cola_obj = tk.Toplevel(self.master)
        self.ventana_cola_obj.title("Gestión de Cola")
        self.ventana_cola_obj.geometry("400x350+950+100")

        tk.Label(self.ventana_cola_obj, text="Elementos de Cola (FIFO):", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.ventana_cola_obj, text="Usuario:", font=("Arial", 12)).pack(pady=2)
        entrada_usuario_cola = tk.Entry(self.ventana_cola_obj, width=30)
        entrada_usuario_cola.pack(pady=2)
        tk.Label(self.ventana_cola_obj, text="Operación:", font=("Arial", 12)).pack(pady=2)
        entrada_operacion_cola = tk.Entry(self.ventana_cola_obj, width=30)
        entrada_operacion_cola.pack(pady=2)

        boton_frame = tk.Frame(self.ventana_cola_obj)
        boton_frame.pack(pady=10)
        tk.Button(boton_frame, text="Agregar a Cola", command=self._agregar_cola_ui).pack(side=tk.LEFT, padx=5)
        tk.Button(boton_frame, text="Eliminar de Cola", command=self._eliminar_cola_ui).pack(side=tk.LEFT, padx=5)

        etiqueta_cola_display = tk.Label(self.ventana_cola_obj, text=f"Cola: {cola_data}", font=("Arial", 12))
        etiqueta_cola_display.pack(pady=10)

    def _agregar_cola_ui(self):
        global entrada_usuario_cola, entrada_operacion_cola, etiqueta_cola_display
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
        global etiqueta_cola_display
        if cola_data:
            usuario_eliminado, operacion_eliminada = cola_data.pop(0)
            etiqueta_cola_display.config(text=f"Cola: {cola_data}")
            messagebox.showinfo("Elemento Eliminado", f"Se eliminó de la Cola: Usuario: {usuario_eliminado}, Operación: {operacion_eliminada}")
        else:
            messagebox.showwarning("Advertencia", "La cola está vacía. No hay elementos para eliminar.")

    # --- Methods for the Tuple window ---
    def mostrar_ventana_tupla(self):
        if self.ventana_tupla_obj and self.ventana_tupla_obj.winfo_exists():
            self.ventana_tupla_obj.lift()
            return

        self.ventana_tupla_obj = tk.Toplevel(self.master)
        self.ventana_tupla_obj.title("Gestión de Tupla")
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
        self.ventana_lista_obj.title("Gestión de Lista")
        self.ventana_lista_obj.geometry("400x300+250+200")

        tk.Label(self.ventana_lista_obj, text="Añadir Elemento a Lista:", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.ventana_lista_obj, text="Elemento:").pack(pady=2)
        self.entry_lista_elemento = tk.Entry(self.ventana_lista_obj, width=30)
        self.entry_lista_elemento.pack(pady=2)

        tk.Button(self.ventana_lista_obj, text="Añadir a Lista", command=self._anadir_lista_ui).pack(pady=5)

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

        tk.Button(self.ventana_conjunto_obj, text="Añadir a Conjunto", command=self._anadir_conjunto_ui).pack(pady=5)

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

    def _convertir_elemento(self, s):
        """Attempts to convert a string to an int or float; otherwise, returns the original string."""
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s

# --- Application entry point ---
if __name__ == "__main__":
    ventana = tk.Tk()
    app = Programa(ventana)
    ventana.mainloop()
