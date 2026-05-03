from fenics import *
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys


# -----------------------------
# Решение Навье–Стокса
# -----------------------------
def solve_navier_stokes(mesh, boundaries, nu=0.01, max_iter=50, tol=1e-6):

    # Taylor–Hood (P2-P1)
    V_el = VectorElement("CG", mesh.ufl_cell(), 2)
    Q_el = FiniteElement("CG", mesh.ufl_cell(), 1)
    W = FunctionSpace(mesh, MixedElement([V_el, Q_el]))

    (u, p) = TrialFunctions(W)
    (v, q) = TestFunctions(W)

    w = Function(W)
    (u_k, p_k) = split(w)

    # Входной профиль
    inflow = Expression(("x[1]", "0.0"), degree=2)

    # Граничные условия
    bcs = [
        DirichletBC(W.sub(0), Constant((0.0, 0.0)), boundaries, 1),  # низ
        DirichletBC(W.sub(0), Constant((0.0, 0.0)), boundaries, 5),  # цилиндр / дуга
        DirichletBC(W.sub(0), Constant((0.0, 0.0)), boundaries, 2),  # верх
        DirichletBC(W.sub(0), inflow, boundaries, 3),                # вход
        DirichletBC(W.sub(1), Constant(0.0), boundaries, 4),         # выход
    ]

    f = Constant((0.0, 0.0))

    # Нелинейная форма (Picard iteration)
    F = (
        inner(dot(u_k, nabla_grad(u)), v) * dx
        + nu * inner(grad(u), grad(v)) * dx
        - div(v) * p * dx
        - q * div(u) * dx
        - inner(f, v) * dx
    )

    a = lhs(F)
    L = rhs(F)

    w_k = Function(W)

    for i in range(max_iter):
        print(f"\nИтерация {i+1}/{max_iter}")

        solve(a == L, w, bcs)

        error = norm(w.vector() - w_k.vector(), 'l2')
        print("Error =", error)

        if error < tol:
            break

        w_k.assign(w)

    u_sol, p_sol = w.split()
    return u_sol, p_sol


# -----------------------------
# Завихрённость
# -----------------------------
def compute_vorticity(u):
    return project(curl(u), FunctionSpace(u.function_space().mesh(), "CG", 1))


def compute_circulation(omega):
    mesh = omega.function_space().mesh()
    return assemble(omega * dx(domain=mesh))


# -----------------------------
# Графики
# -----------------------------
def plot_velocity(u, title="Velocity field", x_limits=None, y_limits=None):
    mesh = u.function_space().mesh()
    coords = mesh.coordinates()
    
    # Если пределы не заданы, используем реальные границы mesh
    if x_limits is None:
        x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
    else:
        x_min, x_max = x_limits
    
    if y_limits is None:
        y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
    else:
        y_min, y_max = y_limits
    
    # Создаем сетку только в области mesh
    nx, ny = 100, 100
    xi = np.linspace(x_min, x_max, nx)
    yi = np.linspace(y_min, y_max, ny)
    X, Y = np.meshgrid(xi, yi)
    
    # Проектируем скорость
    V_cg1 = VectorFunctionSpace(mesh, "CG", 1)
    u_cg1 = project(u, V_cg1)
    
    # Интерполируем
    U = np.zeros((ny, nx))
    Vv = np.zeros((ny, nx))
    
    for i in range(nx):
        for j in range(ny):
            point = Point(X[j, i], Y[j, i])
            try:
                val = u_cg1(point)
                U[j, i] = val[0]
                Vv[j, i] = val[1]
            except:
                U[j, i] = np.nan
                Vv[j, i] = np.nan
    
    # Создаем график
    plt.figure(figsize=(10, 6))
    
    # Маскируем NaN
    mask = np.isnan(U)
    U_masked = np.ma.masked_where(mask, U)
    Vv_masked = np.ma.masked_where(mask, Vv)
    
    plt.streamplot(X, Y, U_masked, Vv_masked, density=2, 
                   linewidth=1, color='b', arrowsize=1)
    
    plt.title(title)
    plt.xlabel('x')
    plt.ylabel('y')
    
    # Важно! Устанавливаем точные пределы
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    
    # НЕ используем axis('equal') - он добавляет пустое пространство
    # Вместо этого сделаем оси пропорциональными, если нужно
    ax = plt.gca()
    ax.set_aspect('equal')  # или 'equal' если хотите сохранить пропорции
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout(pad=0.5)  # Уменьшаем отступы

# -----------------------------
# Основная функция
# -----------------------------
def solve_problem(grid_name, nu):

    mesh = Mesh(f"grids/{grid_name}/grid_{grid_name}.xml")
    boundaries = MeshFunction(
        "size_t", mesh, f"grids/{grid_name}/grid_{grid_name}_facet_region.xml"
    )

    u, p = solve_navier_stokes(mesh, boundaries, nu=nu)

    omega = compute_vorticity(u)
    gamma = compute_circulation(omega)

    return {
        "mesh": mesh,
        "boundaries": boundaries,
        "velocity": u,
        "pressure": p,
        "vorticity": omega,
        "circulation": gamma,
    }

def compute_streamfunction(u, boundaries):
    mesh = u.function_space().mesh()
    
    # Пространство для функции тока
    V_psi = FunctionSpace(mesh, "CG", 2)
    
    # Завихренность
    omega = project(curl(u), V_psi)
    
    # Пробные и тестовые функции
    psi = TrialFunction(V_psi)
    v = TestFunction(V_psi)
    
    a = inner(grad(psi), grad(v)) * dx
    L = omega * v * dx
    
    u_1 = Expression("x[1]", degree=2)
    bc_psi = [
        DirichletBC(V_psi, Constant(0.0), boundaries, 1),  # низ
        DirichletBC(V_psi, Constant(0.0), boundaries, 5),  # цилиндр
        DirichletBC(V_psi, Constant(1.0), boundaries, 2),  # верх
        DirichletBC(V_psi, u_1, boundaries, 3), # Лево (вход)
    ]
    
    # Решение
    psi_sol = Function(V_psi)
    solve(a == L, psi_sol, bc_psi)
    
    return psi_sol

def plot_streamfunction(psi, title="Stream function"):
    plt.figure()
    c = plot(psi, title=title)
    plt.colorbar(c)
    
    mesh = psi.function_space().mesh()
    vertex_values = psi.compute_vertex_values(mesh)
    vertex_coords = mesh.coordinates()
    
    x = vertex_coords[:, 0]
    y = vertex_coords[:, 1]
    values = vertex_values
    
    plt.xlabel('x')
    plt.ylabel('y')
    
    # Контуры функции тока
    plt.tricontour(x, y, values, levels=15, colors='black')
    plt.tricontour(x, y, values, levels=[0], colors='red', linewidths=2)
    
    if values.min() < 0:
        mpl.rcParams['hatch.color'] = 'red'
        plt.tricontourf(
            x, y, values,
            levels=[values.min(), 0],
            hatches=['///'],
            alpha=0,
            colors='none'
        )
    
    return c

# -----------------------------
# MAIN
# -----------------------------
def main():
    grid_name = sys.argv[1]
    nu = float(sys.argv[2])  # вязкость

    result = solve_problem(grid_name, nu)

    print("\n=== RESULTS ===")
    print("Circulation Γ =", result["circulation"])

    plot_velocity(result["velocity"], "Velocity field")
    psi = compute_streamfunction(result["velocity"], result["boundaries"])
    plot_streamfunction(psi)

    plt.show()


if __name__ == "__main__":
    main()
