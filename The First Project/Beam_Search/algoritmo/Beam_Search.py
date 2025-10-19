from Beam_Search.algoritmo.nodo import Node

def h(state, goal):
    """Heurística entre dos estados (state, goal)."""
    x1, y1 = state
    x2, y2 = goal
    return abs(x2 - x1) + abs(y2 - y1)


def reconstruct_path(node):
    """Reconstruye la ruta desde la raíz hasta el nodo dado (lista de nodos)."""
    path = []
    cur = node
    while cur is not None:
        path.append(cur)
        cur = cur.parent
    return list(reversed(path))


def beam_search(problem, start_state, goal_state, beta=3):
    """Beam Search por niveles.
    - problem: objeto que se debe implementar.....
    - start_state, goal_state: estados inicial y meta (tuplas (x,y))
    - beta: ancho del haz (número de nodos que se mantienen por nivel)
    
    Devuelve la lista de nodos desde la raíz hasta la meta, o None si no se encuentra.
    """
    # Nodo raíz
    #Node = globals().get("Node")  # En caso de ejecución fuera del paquete
    root = Node(state=start_state, parent=None, action=None, g=0, h=h(start_state, goal_state), depth=0)
    root.f = root.g + root.h

    # Haz inicial
    beam = [root]

    max_iter = 5000  # límite de seguridad
    iter_count = 0

    while beam:
        iter_count += 1
        if iter_count > max_iter:
            print("⚠️ Límite de iteraciones alcanzado. No hay solución posible.")
            return None

        # Verificar si alguno en el haz actual es meta
        for n in beam:
            if n.state == goal_state:
                return reconstruct_path(n)

        # Expandir todos los nodos del haz y reunir sus hijos
        children = []
        for node in beam:
            try:
                acciones = problem.actions(node.state)
            except Exception:
                acciones = []

            for action in acciones:
                new_state = problem.result(node.state, action)

                # Evitar venenos o celdas inválidas
                if hasattr(problem, "es_veneno") and problem.es_veneno(new_state):
                    continue  # ❌ Saltamos los venenos

                # calcular g: costo acumulado
                c = problem.step_cost(node.state, action, new_state) if hasattr(problem, "step_cost") else 1
                g_new = node.g + c
                h_new = h(new_state, goal_state)

                child = Node(state=new_state, parent=node, action=action, g=g_new, h=h_new, depth=node.depth + 1)
                child.f = child.g + child.h
                children.append(child)

        # Si no hay hijos, terminamos
        if not children:
            print("❌ No hay más caminos válidos. No se encontró solución.")
            return None

        # Seleccionar los beta mejores hijos según f
        children.sort(key=lambda n: n.f)
        beam = children[:beta]

    # No encontrado
    print("❌ No se encontró solución.")
    return None
