from fenics import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import sys


def solve_problem(size, degree):
    size = str(size)
    if size.isdigit():
        directory = size
        prefix = f"grid_{size}"
    elif size.startswith("l_"):
        directory = size
        prefix = f"grid_{size}"
    else:
        directory = size
        prefix = size

    mesh = Mesh(f"grids/{directory}/{prefix}.xml")
    boundaries = MeshFunction(
        "size_t", mesh, f"grids/{directory}/{prefix}_facet_region.xml"
    )

    ds = Measure("ds", subdomain_data=boundaries)

    V = FunctionSpace(mesh, "CG", degree)
    u_1 = Expression("x[1]", degree=degree)

    bcs = [
        DirichletBC(V, Constant(0.0), boundaries, 1),  # Низ
        DirichletBC(V, Constant(0.0), boundaries, 5),  # Низ Дуга
        DirichletBC(V, Constant(1.0), boundaries, 2),  # Верх
        DirichletBC(V, u_1, boundaries, 3), # Лево (вход)
        # Справа (выход) - естественные
    ]

    u = TrialFunction(V)
    v = TestFunction(V)
    f = Constant(0.0)
    a = dot(grad(u), grad(v)) * dx
    L = f * v * dx

    # Решение задачи
    solution = Function(V)
    solve(a == L, solution, bcs)

    #  Циркуляция
    n = FacetNormal(mesh)
    u_n = dot(grad(solution), n)
    Gamma = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=5))

    return {
        "mesh": mesh,
        "boundaries": boundaries,
        "solution": solution,
        "degree": degree,
        "gamma": Gamma,
        "dofs": V.dim(),
    }


def plot_solution(solution, title="Решение"):
    c = plot(solution, title=title)
    plt.colorbar(c)

    mesh = solution.function_space().mesh()
    vertex_values = solution.compute_vertex_values(mesh)  # значения в вершинах
    vertex_coords = mesh.coordinates()  # координаты вершин
    
    x = vertex_coords[:, 0]
    y = vertex_coords[:, 1]
    values = vertex_values
    
    contour = plt.tricontour(x, y, values, 
                         levels=15, 
                         colors='black')
    return c


def main():
    size = sys.argv[1]
    degree = int(sys.argv[2])
    result = solve_problem(size, degree)
    print(result["gamma"])
    plot_solution(result["solution"], title="Решение")
    plt.show()


if __name__ == "__main__":
    main()
