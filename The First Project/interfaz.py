import customtkinter as ctk
from tkinter import messagebox
from constantes import *
from Beam_Search.algoritmo.Beam_Search import beam_search
from Beam_Search.algoritmo.nodo import Node


class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("Beam Search Selection")
        self.root.geometry("770x500")

        self.modo = None
        self.laberinto = []
        self.botones = []
        self.inicio_pos = None
        self.meta_pos = None
        self.camino_actual = []  # 🔹 Guarda el último camino mostrado

        self.GUI()

    def GUI(self):
        panel_superior = ctk.CTkFrame(self.root)
        panel_superior.pack(side="top", fill="x", padx=8, pady=6)

        ctk.CTkLabel(panel_superior, text="Filas:").grid(row=0, column=0, padx=(8, 4))
        self.entry_rows = ctk.CTkEntry(panel_superior, width=70)
        self.entry_rows.grid(row=0, column=1, padx=(0, 8))

        ctk.CTkLabel(panel_superior, text="Columnas:").grid(row=0, column=2, padx=(8, 4))
        self.entry_cols = ctk.CTkEntry(panel_superior, width=70)
        self.entry_cols.grid(row=0, column=3, padx=(0, 8))

        btn_generar = ctk.CTkButton(panel_superior, text="Generar matriz", command=self.matriz_de_seleccion)
        btn_generar.grid(row=0, column=4, padx=8)

        # Botones de modos
        self.btn_inicio = ctk.CTkButton(panel_superior, text="Inicio", command=lambda: self.modo_de_seleccion("Inicio"))
        self.btn_inicio.grid(row=1, column=0, pady=8, padx=4)

        self.btn_veneno = ctk.CTkButton(panel_superior, text="Veneno", command=lambda: self.modo_de_seleccion("Veneno"))
        self.btn_veneno.grid(row=1, column=1, pady=8, padx=4)

        self.btn_meta = ctk.CTkButton(panel_superior, text="Meta", command=lambda: self.modo_de_seleccion("Meta"))
        self.btn_meta.grid(row=1, column=2, pady=8, padx=4)

        self.btn_borrar = ctk.CTkButton(panel_superior, text="Borrar", command=lambda: self.modo_de_seleccion("Borrar"))
        self.btn_borrar.grid(row=1, column=3, pady=8, padx=4)

        btn_limpiar = ctk.CTkButton(panel_superior, text="Limpiar matriz", command=self.limpiar)
        btn_limpiar.grid(row=1, column=4, padx=8)

        btn_beam = ctk.CTkButton(panel_superior, text="Búsqueda Beam Search", command=self.ejecutar_beam_search)
        btn_beam.grid(row=1, column=5, padx=8)

        self.lbl_msg = ctk.CTkLabel(panel_superior, text="Selecciona un modo y haz clic en la matriz.")
        self.lbl_msg.grid(row=2, column=0, columnspan=6, sticky="w", pady=(6, 0), padx=4)

        self.frame_grid = ctk.CTkFrame(self.root)
        self.frame_grid.pack(side="top", fill="both", expand=True, padx=8, pady=8)

    # --------------------------------------------------------------------
    # NUEVAS FUNCIONALIDADES
    # --------------------------------------------------------------------
    def ejecutar_beam_search(self):
        """Ejecuta el algoritmo Beam Search y muestra la animación del camino."""
        if self.inicio_pos is None or self.meta_pos is None:
            messagebox.showwarning("Advertencia", "Selecciona una casilla de inicio y una de meta antes de ejecutar la búsqueda.")
            return

        try:
            problem = self.crear_problema()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el problema: {e}")
            return

        self.lbl_msg.configure(text="🔎 Ejecutando Beam Search...")

        try:
            result = beam_search(problem, self.inicio_pos, self.meta_pos, beta=3)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al ejecutar Beam Search:\n{e}")
            return

        if result is None:
            messagebox.showinfo("Sin solución", "❌ No hay camino posible.")
            return

        path, visited = None, None
        if isinstance(result, tuple) and len(result) >= 2:
            path, visited = result
        else:
            path = result

        if not path:
            messagebox.showinfo("Sin solución", "❌ No hay camino posible.")
            return

        # 🔹 Borrar el camino anterior
        self.borrar_camino_anterior()

        # 🔹 Animar el nuevo camino y mostrar aviso al final
        def al_terminar():
            messagebox.showinfo(
                "Camino encontrado",
                f"✅ Camino encontrado con {len(path)} nodos.\n\n"
                + " → ".join(str(node.state) for node in path)
            )
            self.lbl_msg.configure(text=f"✅ Camino visualizado ({len(path)} pasos).")

        self.mostrar_camino(path, al_terminar)

    def mostrar_camino(self, path, callback=None):
        """Muestra el camino paso a paso y luego ejecuta callback."""
        self.camino_actual = [node.state if hasattr(node, "state") else node for node in path]

        def paso(idx=0):
            if idx < len(self.camino_actual):
                i, j = self.camino_actual[idx]
                if (i, j) not in [self.inicio_pos, self.meta_pos]:
                    self.botones[i][j].configure(fg_color="#3b82f6")
                self.root.after(500, lambda: paso(idx + 1))
            else:
                if callback:
                    callback()

        paso()

    def borrar_camino_anterior(self):
        """Elimina el color azul del camino anterior sin tocar inicio, meta ni venenos."""
        for (i, j) in self.camino_actual:
            if (i, j) not in [self.inicio_pos, self.meta_pos] and self.laberinto[i][j] != VENENO:
                self.set_cell(i, j, VACIA)
        self.camino_actual = []

    # --------------------------------------------------------------------
    # FUNCIONES AUXILIARES ORIGINALES
    # --------------------------------------------------------------------
    def modo_de_seleccion(self, modo):
        self.modo = modo
        self.lbl_msg.configure(text=f"Modo seleccionado: {modo}")

    def crear_problema(self):
        lab = self.laberinto
        filas, cols = self.rows, self.cols

        class Problem:
            def actions(self, state):
                i, j = state
                acciones = []
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < filas and 0 <= nj < cols and lab[ni][nj] != VENENO:
                        acciones.append((di, dj))
                return acciones

            def result(self, state, action):
                i, j = state
                di, dj = action
                return (i + di, j + dj)

        return Problem()

    def matriz_de_seleccion(self):
        try:
            self.rows = int(self.entry_rows.get())
            self.cols = int(self.entry_cols.get())
        except ValueError:
            self.lbl_msg.configure(text="❌ Filas y columnas deben ser enteros.")
            return

        if not (MIN_DIM <= self.rows <= MAX_DIM and MIN_DIM <= self.cols <= MAX_DIM):
            self.lbl_msg.configure(text=f"❌ Dimensiones entre {MIN_DIM} y {MAX_DIM}.")
            return

        self.inicio_pos = None
        self.meta_pos = None
        self.generar_grid()

    def generar_grid(self):
        for i in self.frame_grid.winfo_children():
            i.destroy()

        self.laberinto = [[VACIA for _ in range(self.cols)] for _ in range(self.rows)]
        self.botones = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        frame_centrado = ctk.CTkFrame(self.frame_grid, fg_color="transparent")
        frame_centrado.pack(expand=True)

        cell_size, spacing = 38, 3
        for i in range(self.rows):
            for j in range(self.cols):
                b = ctk.CTkButton(
                    frame_centrado,
                    text="",
                    width=cell_size,
                    height=cell_size,
                    fg_color=COLORES[VACIA],
                    corner_radius=6,
                    border_width=1,
                    border_color="#d1d5db",
                    hover_color="#e2e8f0",
                    command=lambda i=i, j=j: self.click_celda(i, j),
                )
                b.grid(row=i, column=j, padx=spacing, pady=spacing)
                self.botones[i][j] = b

    def click_celda(self, i, j):
        if self.modo == "Veneno":
            if (self.inicio_pos == (i, j)) or (self.meta_pos == (i, j)):
                return
            self.set_cell(i, j, VENENO if self.laberinto[i][j] != VENENO else VACIA)

        elif self.modo == "Inicio":
            if self.inicio_pos and self.inicio_pos != (i, j):
                prev_i, prev_j = self.inicio_pos
                if self.meta_pos != (prev_i, prev_j):
                    self.set_cell(prev_i, prev_j, VACIA)
            if self.laberinto[i][j] == VENENO:
                return
            self.set_cell(i, j, INICIO)
            self.inicio_pos = (i, j)

        elif self.modo == "Meta":
            if self.meta_pos and self.meta_pos != (i, j):
                prev_i, prev_j = self.meta_pos
                if self.inicio_pos != (prev_i, prev_j):
                    self.set_cell(prev_i, prev_j, VACIA)
            if self.laberinto[i][j] == VENENO:
                return
            self.set_cell(i, j, META)
            self.meta_pos = (i, j)

        elif self.modo == "Borrar":
            self.set_cell(i, j, VACIA)
            if self.inicio_pos == (i, j):
                self.inicio_pos = None
            if self.meta_pos == (i, j):
                self.meta_pos = None

    def set_cell(self, i, j, valor):
        self.laberinto[i][j] = valor
        self.botones[i][j].configure(fg_color=COLORES.get(valor, COLORES[VACIA]))

    def limpiar(self):
        if not hasattr(self, "rows"):
            self.lbl_msg.configure(text="⚠️ Primero genera una matriz.")
            return

        self.inicio_pos = None
        self.meta_pos = None
        self.camino_actual = []
        for i in range(self.rows):
            for j in range(self.cols):
                self.set_cell(i, j, VACIA)
        self.lbl_msg.configure(text="🧹 Matriz limpiada.")
