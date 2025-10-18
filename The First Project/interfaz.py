import customtkinter as ctk
from constantes import *


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

        # Construir interfaz
        self.GUI()

    def GUI(self):
        panel_superior = ctk.CTkFrame(self.root)
        panel_superior.pack(side="top", fill="x", padx=8, pady=6)

        # Entradas para tamaño de matriz
        ctk.CTkLabel(panel_superior, text="Filas:").grid(row=0, column=0, padx=(8, 4))
        self.entry_rows = ctk.CTkEntry(panel_superior, width=70)
        self.entry_rows.grid(row=0, column=1, padx=(0, 8))

        ctk.CTkLabel(panel_superior, text="Columnas:").grid(row=0, column=2, padx=(8, 4))
        self.entry_cols = ctk.CTkEntry(panel_superior, width=70)
        self.entry_cols.grid(row=0, column=3, padx=(0, 8))

        btn_generar = ctk.CTkButton(panel_superior, text="Generar matriz", command=self.matriz_de_seleccion)
        btn_generar.grid(row=0, column=4, padx=8)

        # Botones de modo
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

        # Etiqueta informativa
        self.lbl_msg = ctk.CTkLabel(panel_superior, text="Selecciona un modo y haz clic en la matriz.")
        self.lbl_msg.grid(row=2, column=0, columnspan=5, sticky="w", pady=(6, 0), padx=4)

        # Frame para la matriz
        self.frame_grid = ctk.CTkFrame(self.root)
        self.frame_grid.pack(side="top", fill="both", expand=True, padx=8, pady=8)

    def modo_de_seleccion(self, modo):
        self.modo = modo
        self.lbl_msg.configure(
            text=f"Modo actual: {modo.capitalize()}. Click izquierdo para marcar, derecho para borrar."
        )

        for btn, name in [
            (self.btn_inicio, "Inicio"),
            (self.btn_veneno, "Veneno"),
            (self.btn_meta, "Meta"),
            (self.btn_borrar, "Borrar"),
        ]:
            btn.configure(fg_color="#253144" if name == modo else "transparent")

    def matriz_de_seleccion(self):
        try:
            rows = int(self.entry_rows.get())
            cols = int(self.entry_cols.get())
        except ValueError:
            self.lbl_msg.configure(text="❌ Filas y columnas deben ser números enteros.")
            return

        if not (MIN_DIM <= rows <= MAX_DIM and MIN_DIM <= cols <= MAX_DIM):
            self.lbl_msg.configure(text=f"❌ Dimensiones entre {MIN_DIM} y {MAX_DIM}.")
            return

        self.rows = rows
        self.cols = cols
        self.inicio_pos = None
        self.meta_pos = None
        self.generar_grid()

    def generar_grid(self):
        """Genera una matriz centrada y con celdas compactas."""
        # Limpiar contenido previo
        for i in self.frame_grid.winfo_children():
            i.destroy()

        self.laberinto = [[VACIA for _ in range(self.cols)] for _ in range(self.rows)]
        self.botones = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        frame_centrado = ctk.CTkFrame(self.frame_grid, fg_color="transparent")
        frame_centrado.pack(expand=True)

        cell_size = 38
        spacing = 3
        total_width = self.cols * (cell_size + spacing)
        total_height = self.rows * (cell_size + spacing)

        frame_centrado.configure(width=total_width, height=total_height)
        frame_centrado.pack_propagate(False)

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
                b.place(
                    x=j * (cell_size + spacing),
                    y=i * (cell_size + spacing)
                )
                b.bind("<Button-3>", lambda e, i=i, j=j: self.erase_cell(i, j))
                self.botones[i][j] = b

        self.lbl_msg.configure(text=f"Haz clic para marcar según el modo actual: {self.modo}.")

    def click_celda(self, i, j):
        """Acción al hacer clic en una celda según el modo actual"""
        if self.modo == "Veneno":
            # No permitir veneno sobre inicio o meta
            if (self.inicio_pos == (i, j)) or (self.meta_pos == (i, j)):
                return
            if self.laberinto[i][j] == VENENO:
                self.set_cell(i, j, VACIA)
            else:
                self.set_cell(i, j, VENENO)

        elif self.modo == "Inicio":
            # Si ya había un inicio, lo borramos
            if self.inicio_pos and self.inicio_pos != (i, j):
                prev_i, prev_j = self.inicio_pos
                # Solo borrar si no es meta (porque pueden coincidir)
                if self.meta_pos != (prev_i, prev_j):
                    self.set_cell(prev_i, prev_j, VACIA)
            # No permitir sobre veneno
            if self.laberinto[i][j] == VENENO:
                return
            self.set_cell(i, j, INICIO)
            self.inicio_pos = (i, j)

        elif self.modo == "Meta":
            # Si ya había una meta, la borramos
            if self.meta_pos and self.meta_pos != (i, j):
                prev_i, prev_j = self.meta_pos
                # Solo borrar si no es inicio (porque pueden coincidir)
                if self.inicio_pos != (prev_i, prev_j):
                    self.set_cell(prev_i, prev_j, VACIA)
            # No permitir sobre veneno
            if self.laberinto[i][j] == VENENO:
                return
            self.set_cell(i, j, META)
            self.meta_pos = (i, j)

        elif self.modo == "Borrar":
            # Borrar cualquier cosa (pero si era inicio o meta, actualizamos variables)
            self.set_cell(i, j, VACIA)
            if self.inicio_pos == (i, j):
                self.inicio_pos = None
            if self.meta_pos == (i, j):
                self.meta_pos = None

    def erase_cell(self, i, j):
        """Borra celda con clic derecho"""
        self.set_cell(i, j, VACIA)
        if self.inicio_pos == (i, j):
            self.inicio_pos = None
        if self.meta_pos == (i, j):
            self.meta_pos = None

    def set_cell(self, i, j, valor):
        """Actualiza el valor y color de una celda"""
        self.laberinto[i][j] = valor
        color = COLORES.get(valor, COLORES[VACIA])
        self.botones[i][j].configure(fg_color=color)

    def limpiar(self):
        """Reinicia toda la matriz"""
        if not hasattr(self, "rows") or not hasattr(self, "cols"):
            self.lbl_msg.configure(text="⚠️ Primero genera una matriz.")
            return

        self.inicio_pos = None
        self.meta_pos = None
        for i in range(self.rows):
            for j in range(self.cols):
                self.set_cell(i, j, VACIA)
        self.lbl_msg.configure(text="🧹 Matriz limpiada.")
