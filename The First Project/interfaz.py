import customtkinter as ctk
from constantes import *
from Problem import *
from Beam_Search.algoritmo.Beam_Search import *

class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("Beam Search Selection")
        self.root.geometry("850x500")
        self.modo = None
        self.laberinto = []
        self.botones = []
        self.inicio_pos = None
        self.meta_pos = None

        self.GUI()

    def GUI(self):
        panel_superior = ctk.CTkFrame(self.root, corner_radius=15)
        panel_superior.pack(side="top", fill="x", padx=10, pady=10)

        for i in range(7):
            panel_superior.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(panel_superior, text="Filas:").grid(row=0, column=0, padx=(5, 2), pady=6, sticky="e")
        self.entry_rows = ctk.CTkEntry(panel_superior, width=70, justify="center")
        self.entry_rows.grid(row=0, column=1, padx=3, pady=6)

        ctk.CTkLabel(panel_superior, text="Columnas:").grid(row=0, column=2, padx=(5, 2), pady=6, sticky="e")
        self.entry_cols = ctk.CTkEntry(panel_superior, width=70, justify="center")
        self.entry_cols.grid(row=0, column=3, padx=3, pady=6)

        ctk.CTkLabel(panel_superior, text="Beta:").grid(row=0, column=4, padx=(5, 2), pady=6, sticky="e")
        self.entry_beta = ctk.CTkEntry(panel_superior, width=70, justify="center")
        self.entry_beta.grid(row=0, column=5, padx=3, pady=6)

        btn_generar = ctk.CTkButton(panel_superior, text="🧩 Generar matriz", width=140, command=self.matriz_de_seleccion)
        btn_generar.grid(row=0, column=6, padx=10, pady=6, sticky="e")

        modo_frame = ctk.CTkFrame(panel_superior, fg_color="transparent")
        modo_frame.grid(row=1, column=0, columnspan=7, pady=8, sticky="ew")


        for i in range(6):
            modo_frame.grid_columnconfigure(i, weight=1)

        self.btn_inicio = ctk.CTkButton(modo_frame, text="🚩 Inicio", command=lambda: self.modo_de_seleccion("Inicio"))
        self.btn_inicio.grid(row=0, column=0, padx=4, pady=6, sticky="ew")

        self.btn_veneno = ctk.CTkButton(modo_frame, text="☠️ Veneno", command=lambda: self.modo_de_seleccion("Veneno"))
        self.btn_veneno.grid(row=0, column=1, padx=4, pady=6, sticky="ew")

        self.btn_meta = ctk.CTkButton(modo_frame, text="🎯 Meta", command=lambda: self.modo_de_seleccion("Meta"))
        self.btn_meta.grid(row=0, column=2, padx=4, pady=6, sticky="ew")

        btn_limpiar = ctk.CTkButton(modo_frame, text="🧹 Limpiar", command=self.limpiar)
        btn_limpiar.grid(row=0, column=3, padx=4, pady=6, sticky="ew")

        btn_ejecutar = ctk.CTkButton(modo_frame, text="⚙️ Ejecutar Beam Search", fg_color="#1E88E5", hover_color="#1565C0", command=self.ejecutar_beam_search)
        btn_ejecutar.grid(row=0, column=4, padx=4, pady=6, sticky="ew")

        self.lbl_msg = ctk.CTkLabel(panel_superior, text="💡 Selecciona un modo y haz clic en la matriz.", anchor="w", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_msg.grid(row=2, column=0, columnspan=7, sticky="w", padx=8, pady=(5, 2))

        self.frame_grid = ctk.CTkFrame(self.root, corner_radius=15)
        self.frame_grid.pack(side="top", fill="both", expand=True, padx=12, pady=10)


    def modo_de_seleccion(self, modo):
        self.modo = modo
        self.lbl_msg.configure(
            text=f"Modo actual: {modo}"
        )

        for btn, name in [
            (self.btn_inicio, "Inicio"),
            (self.btn_veneno, "Veneno"),
            (self.btn_meta, "Meta"),
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
        self.generar_matriz()

    def generar_matriz(self):
        """Genera una matriz centrada y con celdas compactas."""
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
                button = ctk.CTkButton(
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
                button.place(
                    x=j * (cell_size + spacing),
                    y=i * (cell_size + spacing)
                )
                button.bind("<Button-3>", lambda e, i=i, j=j: self.erase_cell(i, j))
                self.botones[i][j] = button

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

    def ejecutar_beam_search(self):
        """Ejecuta el algoritmo Beam Search sobre la matriz actual."""
        if not self.inicio_pos or not self.meta_pos:
            self.lbl_msg.configure(text="⚠️ Debes marcar un inicio y una meta.")
            return
        
        try:
            problem = Problem(self.laberinto)
            start_state = self.inicio_pos
            goal_state = self.meta_pos
            beta = int(self.entry_beta.get())
            ruta = beam_search(problem, start_state, goal_state, beta=beta)
        except Exception as e:
            self.lbl_msg.configure(text=f"❌ Error ejecutando Beam Search: {e}")
            return
        if not ruta:
            self.lbl_msg.configure(text="⚠️ No se encontró un camino.")
            return

        def pintar_paso(index):
            if index >= len(ruta):
                return 
            
            nodo = ruta[index]
            i, j = nodo.state
            if nodo.parent != None:
                print(nodo.parent)
            else:
                print(f"{nodo.state} es la raíz")
            if (i, j) != self.inicio_pos and (i, j) != self.meta_pos:
                self.set_cell(i, j, CAMINO)

            self.root.after(500, lambda: pintar_paso(index + 1))

        pintar_paso(0)

