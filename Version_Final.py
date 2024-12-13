import tkinter as tk
from tkinter import messagebox
import sqlite3

# Configuración de la base de datos
def inicializar_bd():
    conn = sqlite3.connect("procesadores.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS procesadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT,
        modelo TEXT,
        tipo TEXT,
        uso TEXT,
        nucleos INTEGER,
        hilos INTEGER,
        precio TEXT
    )''')
    conn.commit()
    conn.close()

# Operaciones en la base de datos
def agregar_procesador_bd(procesador):
    conn = sqlite3.connect("procesadores.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO procesadores (marca, modelo, tipo, uso, nucleos, hilos, precio)
                      VALUES (:Marca, :Modelo, :Tipo, :Uso, :Nucleos, :Hilos, :Precio)''', procesador)
    conn.commit()
    conn.close()

def obtener_procesadores_bd():
    conn = sqlite3.connect("procesadores.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM procesadores')
    datos = cursor.fetchall()
    conn.close()
    return datos

def eliminar_procesador_bd(procesador_id):
    conn = sqlite3.connect("procesadores.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM procesadores WHERE id = ?', (procesador_id,))
    conn.commit()
    conn.close()

# Interfaz gráfica
class SistemaExpertoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tu Procesador Ideal")

        # Texto principal
        tk.Label(root, text="Tu Procesador Ideal", font=("Arial", 24)).pack(pady=20)

        # Botones principales
        tk.Button(root, text="Encontrar Tu Procesador", command=self.encontrar_procesador, width=25).pack(pady=10)
        tk.Button(root, text="Agregar Procesador", command=self.agregar_procesador, width=25).pack(pady=10)

    def agregar_procesador(self):
        """Ventana para agregar un procesador."""
        agregar_window = tk.Toplevel(self.root)
        agregar_window.title("Agregar Procesador")

        # Etiquetas y campos de entrada
        campos = ["Marca", "Modelo", "Tipo", "Uso", "Nucleos", "Hilos", "Precio"]
        entradas = {}

        for campo in campos:
            tk.Label(agregar_window, text=f"{campo}:").pack()
            entrada = tk.Entry(agregar_window)
            entrada.pack()
            entradas[campo] = entrada

        def guardar():
            procesador = {}

            for campo in ["Marca", "Modelo", "Tipo", "Uso", "Precio"]:
                procesador[campo] = entradas[campo].get().strip()

            if procesador["Tipo"] not in ["Portátil", "Escritorio"]:
                messagebox.showerror("Error", "El campo 'Tipo' debe ser 'Portátil' o 'Escritorio'.")
                return

            if procesador["Precio"] not in ["bajo", "medio", "alto"]:
                messagebox.showerror("Error", "El campo 'Precio' debe ser 'bajo', 'medio' o 'alto'.")
                return

            try:
                procesador["Nucleos"] = int(entradas["Nucleos"].get().strip())
                procesador["Hilos"] = int(entradas["Hilos"].get().strip())
            except ValueError:
                messagebox.showerror("Error", "Núcleos e Hilos deben ser números enteros.")
                return

            if all(procesador.values()):
                agregar_procesador_bd(procesador)
                messagebox.showinfo("Éxito", "Procesador agregado correctamente")
                agregar_window.destroy()
            else:
                messagebox.showerror("Error", "Todos los campos son obligatorios.")

        tk.Button(agregar_window, text="Guardar", command=guardar).pack(pady=10)

        def eliminar_procesador():
            eliminar_window = tk.Toplevel(agregar_window)
            eliminar_window.title("Eliminar Procesador")

            datos = obtener_procesadores_bd()
            if not datos:
                messagebox.showinfo("Información", "No hay procesadores en la base de datos.")
                eliminar_window.destroy()
                return

            tk.Label(eliminar_window, text="Seleccione un procesador para eliminar:").pack()
            frame_scroll = tk.Frame(eliminar_window)
            frame_scroll.pack(fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(frame_scroll)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            lista = tk.Listbox(frame_scroll, width=100, yscrollcommand=scrollbar.set)
            lista.pack(fill=tk.BOTH, expand=True)

            scrollbar.config(command=lista.yview)

            for procesador in datos:
                lista.insert(tk.END, f"ID: {procesador[0]} - Marca: {procesador[1]} - Modelo: {procesador[2]} - Tipo: {procesador[3]} - Uso: {procesador[4]} - Núcleos: {procesador[5]} - Hilos: {procesador[6]} - Precio: {procesador[7]}")

            def eliminar():
                seleccion = lista.curselection()
                if seleccion:
                    procesador_id = datos[seleccion[0]][0]
                    eliminar_procesador_bd(procesador_id)
                    messagebox.showinfo("Éxito", "Procesador eliminado correctamente")
                    eliminar_window.destroy()
                else:
                    messagebox.showerror("Error", "Seleccione un procesador para eliminar.")

            tk.Button(eliminar_window, text="Eliminar", command=eliminar).pack(pady=10)

        tk.Button(agregar_window, text="Eliminar Procesador", command=eliminar_procesador).pack(pady=10)

    def encontrar_procesador(self):
        """Ventana para encontrar un procesador."""
        buscar_window = tk.Toplevel(self.root)
        buscar_window.title("Encontrar Procesador")

        consultas = [
            ("De qué rango de precios buscas? (bajo, medio, alto)", "Precio", ["bajo", "medio", "alto"]),
            ("De qué marca buscas?", "Marca", None),
            ("¿Portátil o Escritorio?", "Tipo", ["Portátil", "Escritorio"]),
            ("¿Lo utilizarás para ofimática, juegos o trabajos pesados?", "Uso", None),
        ]
        respuestas = {}

        def realizar_pregunta(indice):
            if indice >= len(consultas):
                # Búsqueda final
                conn = sqlite3.connect("procesadores.db")
                cursor = conn.cursor()

                query = "SELECT * FROM procesadores WHERE " + " AND ".join(
                    [f"{clave.lower()} = ?" for clave in respuestas.keys()]
                )
                cursor.execute(query, tuple(respuestas.values()))
                resultados = cursor.fetchall()
                conn.close()

                if resultados:
                    resultado_texto = "\n".join([
                        f"Modelo: {r[2]} - {r[1]} ({r[3]}), {r[5]} núcleos, {r[6]} hilos, precio: {r[7]}, uso: {r[4]}"
                        for r in resultados
                    ])
                    messagebox.showinfo("Resultados", resultado_texto)
                else:
                    messagebox.showinfo("Resultados", "No se encontró un procesador que coincida.")
                buscar_window.destroy()
                return

            # Crear pregunta
            pregunta, clave, opciones_validas = consultas[indice]

            for widget in buscar_window.winfo_children():
                widget.destroy()

            tk.Label(buscar_window, text=pregunta).pack()
            entrada = tk.Entry(buscar_window)
            entrada.pack()

            def guardar_respuesta():
                respuesta = entrada.get().strip()
                if opciones_validas and respuesta not in opciones_validas:
                    messagebox.showerror("Error", f"La respuesta debe ser una de las siguientes: {', '.join(opciones_validas)}.")
                    return

                respuestas[clave] = respuesta
                realizar_pregunta(indice + 1)

            tk.Button(buscar_window, text="Siguiente", command=guardar_respuesta).pack(pady=10)

        # Iniciar la primera pregunta
        realizar_pregunta(0)

# Inicializar la base de datos y ejecutar la aplicación
if __name__ == "__main__":
    inicializar_bd()
    root = tk.Tk()
    app = SistemaExpertoApp(root)
    root.mainloop()
