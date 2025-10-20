from Beam_Search.algoritmo.nodo import *
from Manhattan import *

def reconstruct_path(node):
    path = []
    current = node
    while current is not None:
        path.append(current)
        current = current.parent
    return list(reversed(path))

def beam_search(problem, start_state, goal_state, beta=0):
    root = Node(state=start_state, parent=None, action=None, g=0, h=heuristic(start_state, goal_state))
    root.f = root.g + root.h

    beam = [root]
    visited_states = set()

    while beam:
        for node in beam:
            if node.state == goal_state:
                return reconstruct_path(node)

        children = []
        for node in beam:
            if node.state in visited_states:
                continue
            visited_states.add(node.state)

            for action in problem.actions(node.state):
                new_state = action  
                if new_state in visited_states:
                    continue

                cost = problem.step_cost(node.state, new_state) 
                new_g = node.g + cost
                child = Node(state=new_state, parent=node, action=action,g=new_g, h=heuristic(new_state, goal_state))
                child.f = child.g + child.h
                children.append(child)

        if not children:
            return None

        children.sort(key=lambda n: n.f)
        beam = children[:beta]

    return None
