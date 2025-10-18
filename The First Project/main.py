from interfaz import Interfaz
import customtkinter as ctk

if __name__ == "__main__":
    gui = ctk.CTk()
    app = Interfaz(gui)
    gui.mainloop()