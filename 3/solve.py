from fenics import *
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys


def get_l2_from_mesh(mesh, boundaries, arc_id=5):
    coords = mesh.coordinates()
    arc_x_coords = []
    for facet in facets(mesh):
        if facet.exterior():
            marker = boundaries[facet.index()]
            if marker == arc_id:
                vertices = facet.entities(0)
                for v in vertices:
                    point = coords[v]
                    if point[1] == 0:
                        arc_x_coords.append(point[0])
    l2 = np.max(arc_x_coords)
    return l2


def get_obstacle_radius_from_mesh(mesh, boundaries, arc_id=5):
    coords = mesh.coordinates()
    xs = []
    ys = []

    for facet in facets(mesh):
        if facet.exterior():
            marker = boundaries[facet.index()]
            if marker == arc_id:
                vertices = facet.entities(0)
                for v in vertices:
                    point = coords[v]
                    xs.append(point[0])
                    ys.append(point[1])

    if not xs:
        return 0.5

    width = max(xs) - min(xs)
    height = max(ys) - min(ys)

    radius = 0.5 * max(width, height)

    if radius <= 1e-12:
        return 0.5

    return float(radius)


def solve_poisson(V, bcs, source, solution):
    u = TrialFunction(V)
    v = TestFunction(V)

    a = dot(grad(u), grad(v)) * dx
    L = source * v * dx

    solve(a == L, solution, bcs)

    return solution


def compute_vortex_area(psi, mesh, dx):
    V_dg0 = FunctionSpace(mesh, "DG", 0)  # Кусочно-постоянные функции
    indicator = Function(V_dg0)

    psi_dg0 = interpolate(psi, V_dg0)

    psi_values = psi_dg0.vector().get_local()
    indicator_values = np.where(psi_values < 0, 1.0, 0.0)
    indicator.vector().set_local(indicator_values)
    indicator.vector().apply("insert")

    area = assemble(indicator * dx)

    return area


class WakeZone(UserExpression):
    def __init__(self, l2, r_cyl, psi_value, **kwargs):
        super().__init__(**kwargs)
        self.l2 = l2
        self.r_cyl = r_cyl
        self.psi_value = psi_value

    def eval(self, values, x):
        if x[0] > self.l2 and x[0] < self.l2 + self.r_cyl and x[1] < self.r_cyl:
            values[0] = self.psi_value
        else:
            values[0] = 0.0

    def value_shape(self):
        return ()


def compute_vorticity_field(psi, gamma, vortex_area):
    V = psi.function_space()
    omega = Function(V)

    psi_values = psi.vector().get_local()
    omega_value = gamma / vortex_area if vortex_area > 1e-12 else 0.0
    omega_values = np.where(psi_values < 0, omega_value, 0.0)

    omega.vector().set_local(omega_values)
    omega.vector().apply("insert")

    return omega


def compute_circulation_from_vorticity(psi, omega, dx):
    circulation = assemble(conditional(lt(psi, 0.0), omega, 0.0) * dx)
    return circulation


def solve_problem(grid_name, degree, gamma=-1.0, max_iter=100, tol=1e-6):
    mesh = Mesh(f"grids/{grid_name}/grid_{grid_name}.xml")
    boundaries = MeshFunction(
        "size_t", mesh, f"grids/{grid_name}/grid_{grid_name}_facet_region.xml"
    )

    V = FunctionSpace(mesh, "CG", degree)
    u_1 = Expression("x[1]", degree=degree)

    bcs = [
        DirichletBC(V, Constant(0.0), boundaries, 1),  # Низ
        DirichletBC(V, Constant(0.0), boundaries, 5),  # Дуга
        DirichletBC(V, Constant(1.0), boundaries, 2),  # Верх
        DirichletBC(V, u_1, boundaries, 3),  # Вход
        # Справа выход — естественное граничное условие
    ]

    psi = Function(V)

    # Потенциальное решение
    solve_poisson(V, bcs, Constant(0.0), psi)

    l2 = get_l2_from_mesh(mesh, boundaries)
    r_cyl = get_obstacle_radius_from_mesh(mesh, boundaries)

    print("l2 =", l2)
    print("r_cyl =", r_cyl)

    # Начальная вихревая область
    wake_zone = WakeZone(
        l2=l2,
        r_cyl=r_cyl,
        psi_value=-0.05,
        degree=degree,
    )

    psi.vector().axpy(1.0, interpolate(wake_zone, V).vector())

    history = []
    omega = Function(V)

    for k in range(max_iter):
        print(f"\nИтерация {k + 1}/{max_iter}")

        vortex_area = compute_vortex_area(psi, mesh, dx)
        print("Vortex area =", vortex_area)

        omega_value = gamma / vortex_area if vortex_area > 1e-12 else 0.0

        psi_values = psi.vector().get_local()
        omega_values = np.where(psi_values < 0, omega_value, 0.0)

        omega.vector().set_local(omega_values)
        omega.vector().apply("insert")

        psi_new = Function(V)
        psi_new.assign(psi)

        solve_poisson(V, bcs, omega, psi_new)

        error = errornorm(psi_new, psi, "L2")
        print("Error =", error)

        history.append(
            {
                "iteration": k + 1,
                "vortex_area": float(vortex_area),
                "omega_value": float(omega_value),
                "error": float(error),
            }
        )

        psi.assign(psi_new)

        if error < tol:
            break

    final_vortex_area = compute_vortex_area(psi, mesh, dx)
    final_omega_value = gamma / final_vortex_area if final_vortex_area > 1e-12 else 0.0
    final_omega = compute_vorticity_field(psi, gamma, final_vortex_area)
    final_gamma = compute_circulation_from_vorticity(psi, final_omega, dx)

    return {
        "mesh": mesh,
        "boundaries": boundaries,
        "solution": psi,
        "vorticity": final_omega,
        "vorticity_gamma": final_gamma,
        "degree": degree,
        "dofs": V.dim(),
        "iterations": len(history),
        "error_final": history[-1]["error"] if history else None,
        "vortex_area": float(final_vortex_area),
        "omega_value": float(final_omega_value),
        "history": history,
    }


def plot_solution(solution, title="Решение"):
    plt.figure()
    c = plot(solution, title=title)
    plt.colorbar(c)

    mesh = solution.function_space().mesh()
    vertex_values = solution.compute_vertex_values(mesh)  # значения в вершинах
    vertex_coords = mesh.coordinates()  # координаты вершин

    x = vertex_coords[:, 0]
    y = vertex_coords[:, 1]
    values = vertex_values

    plt.xlabel("x1")
    plt.ylabel("x2")

    mpl.rcParams["hatch.color"] = "red"
    plt.tricontourf(
        x,
        y,
        values,
        levels=[values.min(), 0],  # область ниже нуля
        hatches=["///"],  # тип штриховки
        alpha=0,
    )

    plt.tricontour(x, y, values, levels=15, colors="black")
    plt.tricontour(x, y, values, levels=[0], colors="red", linewidths=2)

    return c


def plot_vorticity(result, title):
    plt.figure()
    c = plot(result, title=title)
    plt.colorbar(c)


def main():
    grid_name = sys.argv[1]
    degree = int(sys.argv[2])
    gamma = float(sys.argv[3])
    result = solve_problem(grid_name, degree, gamma=gamma, tol=1e-3)
    print("Final gamma: ", result["vorticity_gamma"])
    plot_solution(result["solution"], title=f"Функция тока: Г = {gamma}")
    plot_vorticity(result["vorticity"], title=f"Завихрённость: Г = {gamma}")
    plt.show()


if __name__ == "__main__":
    main()
