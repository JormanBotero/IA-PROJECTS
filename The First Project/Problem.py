from constantes import *

class Problem:
    def __init__(self, matriz):
        self.matriz = matriz
        self.filas = len(matriz)
        self.columnas = len(matriz[0])

    def actions(self, state):
        x, y = state
        actions = []
        for mov_x, mov_y in [(-1,0), (1,0), (0,-1), (0,1)]:
            new_x, new_y = x + mov_x, y + mov_y
            if 0 <= new_x < self.filas and 0 <= new_y < self.columnas:
                actions.append((new_x, new_y))
        return actions

    def step_cost(self, state, action):
        i, j = action
        return 4 if self.matriz[i][j] == VENENO else 1
