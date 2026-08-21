import z3


def _build_candidate_edges(atoms, rows, cols):
    edges = []

    for row in range(rows + 1):
        last_atom = None
        for col in range(cols + 1):
            atom = atoms[row][col]
            if atom.state == 0:
                continue
            if last_atom is not None:
                edges.append((last_atom, atom, "H"))
            last_atom = atom

    for col in range(cols + 1):
        last_atom = None
        for row in range(rows + 1):
            atom = atoms[row][col]
            if atom.state == 0:
                continue
            if last_atom is not None:
                edges.append((last_atom, atom, "V"))
            last_atom = atom

    return edges


def _edges_cross(edge_a, edge_b):
    a1, a2, orientation_a = edge_a
    b1, b2, orientation_b = edge_b

    if orientation_a == orientation_b:
        return False

    if orientation_a == "H":
        h1, h2, v1, v2 = a1, a2, b1, b2
    else:
        h1, h2, v1, v2 = b1, b2, a1, a2

    row = h1.row
    col = v1.col

    col_lo, col_hi = sorted((h1.col, h2.col))
    row_lo, row_hi = sorted((v1.row, v2.row))

    return col_lo < col < col_hi and row_lo < row < row_hi


def solve_atoms(atoms, rows, cols):
    atom_list = [atom for atom_row in atoms for atom in atom_row if atom.state != 0]

    if len(atom_list) == 0:
        return False, "Place at least one atom before solving", []

    if len(atom_list) == 1:
        return False, "A single atom cannot be connected to anything", []

    candidate_edges = _build_candidate_edges(atoms, rows, cols)

    if len(candidate_edges) == 0:
        return False, "No atoms are in line with each other", []

    solver = z3.Solver()

    edge_vars = {}
    for atom1, atom2, orientation in candidate_edges:
        line_var = z3.Int(f"lines_{atom1.row}_{atom1.col}_{atom2.row}_{atom2.col}")
        solver.add(line_var >= 0, line_var <= 2)
        edge_vars[(atom1, atom2)] = (line_var, orientation)

    incident_vars = {atom: [] for atom in atom_list}
    neighbors = {atom: [] for atom in atom_list}
    for (atom1, atom2), (line_var, orientation) in edge_vars.items():
        incident_vars[atom1].append(line_var)
        incident_vars[atom2].append(line_var)
        neighbors[atom1].append((atom2, line_var))
        neighbors[atom2].append((atom1, line_var))

    for atom in atom_list:
        solver.add(z3.Sum(incident_vars[atom]) == atom.state)

    for i in range(len(candidate_edges)):
        for j in range(i + 1, len(candidate_edges)):
            if _edges_cross(candidate_edges[i], candidate_edges[j]):
                var_i = edge_vars[(candidate_edges[i][0], candidate_edges[i][1])][0]
                var_j = edge_vars[(candidate_edges[j][0], candidate_edges[j][1])][0]
                solver.add(z3.Or(var_i == 0, var_j == 0))

    root = atom_list[0]
    order = {atom: z3.Int(f"order_{atom.row}_{atom.col}") for atom in atom_list}
    solver.add(order[root] == 0)

    for atom in atom_list:
        if atom is root:
            continue

        solver.add(order[atom] >= 1, order[atom] <= len(atom_list) - 1)

        reachable_from = [
            z3.And(line_var > 0, order[neighbor] == order[atom] - 1)
            for neighbor, line_var in neighbors[atom]
        ]
        if reachable_from:
            solver.add(z3.Or(reachable_from))
        else:
            solver.add(False)

    if solver.check() != z3.sat:
        return False, "This puzzle has no solution", []

    model = solver.model()

    solution_edges = []
    for (atom1, atom2), (line_var, orientation) in edge_vars.items():
        line_count = model.evaluate(line_var).as_long()
        if line_count > 0:
            solution_edges.append((atom1, atom2, orientation, line_count))

    return True, None, solution_edges