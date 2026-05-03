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
                    arc_x_coords.append(point[0])
    return np.max(arc_x_coords)


def solve_poisson(V, bcs, source, solution):
    u = TrialFunction(V)
    v = TestFunction(V)

    a = dot(grad(u), grad(v)) * dx
    L = source * v * dx

    solve(a == L, solution, bcs)
    return solution


# Разделение вихревой области на верхнюю и нижнюю части
def compute_vortex_areas(psi, mesh, dx, yc):
    V_dg0 = FunctionSpace(mesh, "DG", 0)

    psi_dg0 = interpolate(psi, V_dg0)
    psi_vals = psi_dg0.vector().get_local()
    coords = V_dg0.tabulate_dof_coordinates()

    top = np.where((psi_vals < 0) & (coords[:, 1] > yc), 1.0, 0.0)
    bottom = np.where((psi_vals < 0) & (coords[:, 1] < yc), 1.0, 0.0)

    f_top = Function(V_dg0)
    f_bot = Function(V_dg0)

    f_top.vector().set_local(top)
    f_bot.vector().set_local(bottom)

    f_top.vector().apply("insert")
    f_bot.vector().apply("insert")

    A_top = assemble(f_top * dx)
    A_bot = assemble(f_bot * dx)

    return A_top, A_bot


class WakeZone(UserExpression):
    def __init__(self, xc, yc, r_cyl, psi_value, **kwargs):
        super().__init__(**kwargs)
        self.xc = xc
        self.yc = yc
        self.r_cyl = r_cyl
        self.psi_value = psi_value

    def eval(self, values, x):
        if (x[0] > self.xc and x[0] < self.xc + self.r_cyl) and  \
           (x[1] > self.yc and x[1] < self.yc + self.r_cyl):
            values[0] = self.psi_value
        else:
            values[0] = 0.0

    def value_shape(self):
        return ()


def compute_circulation_from_vorticity(psi, omega, dx):
    return assemble(conditional(lt(psi, 0.0), omega, 0.0) * dx)


def solve_problem(grid_name, degree, gamma_top=-1.0, gamma_bot=1.0, max_iter=100, tol=1e-6):
    mesh = Mesh(f"grids/{grid_name}/grid_{grid_name}.xml")
    boundaries = MeshFunction(
        "size_t", mesh, f"grids/{grid_name}/grid_{grid_name}_facet_region.xml"
    )

    V = FunctionSpace(mesh, "CG", degree)
    u_1 = Expression("x[1]", degree=degree)

    bcs = [
        DirichletBC(V, Constant(0.0), boundaries, 1),
        DirichletBC(V, Constant(1.0), boundaries, 5),
        DirichletBC(V, Constant(2.0), boundaries, 2),
        DirichletBC(V, u_1, boundaries, 3),
    ]

    psi = Function(V)

    solve_poisson(V, bcs, Constant(0.0), psi)

    l2 = get_l2_from_mesh(mesh, boundaries)
    print("l2 =", l2)

    yc = 1
    rc = 0.5

    wake_top = WakeZone(l2, yc - rc, rc, -2, degree=degree)
    wake_bot = WakeZone(l2, yc, rc, -2, degree=degree)

    psi.vector().axpy(1.0, interpolate(wake_top, V).vector())
    psi.vector().axpy(1.0, interpolate(wake_bot, V).vector())

    for k in range(max_iter):
        print(f"\nИтерация {k+1}/{max_iter}")

        A_top, A_bot = compute_vortex_areas(psi, mesh, dx, yc)

        print("A_top =", A_top, "A_bot =", A_bot)

        omega_top = gamma_top / A_top if A_top > 1e-12 else 0.0
        omega_bot = gamma_bot / A_bot if A_bot > 1e-12 else 0.0

        omega = Function(V)

        psi_vals = psi.vector().get_local()
        coords = V.tabulate_dof_coordinates()

        omega_vals = np.zeros_like(psi_vals)

        for i in range(len(psi_vals)):
            if psi_vals[i] < 0:
                if coords[i, 1] > yc:
                    omega_vals[i] = omega_top
                else:
                    omega_vals[i] = omega_bot

        omega.vector().set_local(omega_vals)
        omega.vector().apply("insert")

        psi_new = Function(V)
        solve_poisson(V, bcs, omega, psi_new)

        error = errornorm(psi_new, psi, "L2")
        print("Error =", error)

        psi.assign(psi_new)

        if error < tol:
            break

    return {
        "mesh": mesh,
        "solution": psi,
        "vorticity": omega
    }


def plot_solution(solution, title="Решение"):
    plt.figure()
    c = plot(solution, title=title)
    plt.colorbar(c)

    mesh = solution.function_space().mesh()
    vertex_values = solution.compute_vertex_values(mesh)
    coords = mesh.coordinates()

    x = coords[:, 0]
    y = coords[:, 1]

    plt.tricontour(x, y, vertex_values, levels=15, colors="black")

    mpl.rcParams["hatch.color"] = "red"

    try:
        plt.tricontourf(
            x, y, vertex_values,
            levels=[vertex_values.min(), 0],
            hatches=["///"],
            alpha=0
        )
        plt.tricontour(x, y, vertex_values, levels=[0], colors="red", linewidths=2)
    except:
        pass

    return c


def main():
    grid_name = sys.argv[1]
    degree = int(sys.argv[2])
    gamma_top = float(sys.argv[3])
    gamma_bot = float(sys.argv[4])

    result = solve_problem(grid_name, degree, gamma_top, gamma_bot, tol=1e-3)

    plot_solution(result["solution"], title=f"psi, Gamma={gamma_top}, {gamma_bot}")
    plt.show()


if __name__ == "__main__":
    main()
