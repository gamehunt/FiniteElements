from fenics import *
import matplotlib.pyplot as plt
import sys

def solve_problem(size, degree):
    size = str(size)
    if size.isdigit():
        directory = size
        prefix = f'grid_{size}'
    elif size.startswith('l_'):
        directory = size
        prefix = f'grid_{size}'
    else:
        directory = size
        prefix = size

    mesh = Mesh(f'mesh/{directory}/{prefix}.xml')
    boundaries = MeshFunction("size_t", mesh, f'mesh/{directory}/{prefix}_facet_region.xml')

    ds = Measure("ds", subdomain_data=boundaries)

    V = FunctionSpace(mesh, "CG", degree)

    # Условие на входе в канал
    u_1 = Expression("x[1]", degree=degree)

    # Граничные условия
    bcs = [DirichletBC(V, Constant(0.0), boundaries, 1), # Низ
           DirichletBC(V, Constant(1.0), boundaries, 2), # Верх
           DirichletBC(V, Constant(0.5), boundaries, 5), # Цилиндр 1
           DirichletBC(V, Constant(0.5), boundaries, 6), # Цилиндр 2
           DirichletBC(V, u_1, boundaries, 3)] # Лево (вход)
    # На выходе естественные граничные условия (вроде)

    # Вариационная задача
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
    Gamma1 = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=5))
    Gamma2 = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=6))

    return {
        "mesh": mesh,
        "boundaries": boundaries,
        "solution": solution,
        "degree": degree,
        "gamma1": Gamma1,
        "gamma2": Gamma2,
        "dofs": V.dim(),
    }


def plot_solution(result, title="Решение"):
    c = plot(result["solution"], title=title)
    plt.colorbar(c)
    return c


def main():
    size = sys.argv[1]
    degree = int(sys.argv[2])
    result = solve_problem(size, degree)
    print(result["gamma1"], result["gamma2"])
    plot_solution(result, title="Решение")
    plt.show()


if __name__ == "__main__":
    main()
