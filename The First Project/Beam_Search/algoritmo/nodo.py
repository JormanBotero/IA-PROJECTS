# nodo.py - Clase Node mejorada (en español)
class Node:
    """Nodo usado en el árbol de búsqueda para Beam Search.

    Atributos:
        state: representación del estado (por ejemplo, coordenadas (x,y)).
        parent: referencia al nodo padre (otro Node) o None si es la raíz.
        action: acción aplicada desde el padre para llegar a este nodo.
        g: costo acumulado desde la raíz hasta este nodo (g(n)).
        h: valor heurístico estimado desde este nodo hasta la meta (h(n)).
        f: puntuación usada para ordenar/seleccionar nodos (por defecto f = g + h).
        depth: profundidad en el árbol (0 para la raíz).
    """
    def __init__(self, state=None, parent=None, action=None, g=0, h=0, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h
        self.f = g + h
        self.depth = depth

    def __repr__(self):
        return f"Node(state={self.state}, g={self.g}, h={self.h}, f={self.f}, depth={self.depth})"

    def __str__(self):
        return str(self.state)
