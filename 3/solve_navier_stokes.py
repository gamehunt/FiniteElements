from fenics import *
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import json
import shutil

# -----------------------------
# Решение Навье–Стокса
# -----------------------------
def solve_navier_stokes(mesh, boundaries, nu=0.01):

    # Taylor–Hood (P2-P1)
    V_el = VectorElement("CG", mesh.ufl_cell(), 2)
    Q_el = FiniteElement("CG", mesh.ufl_cell(), 1)
    W = FunctionSpace(mesh, MixedElement([V_el, Q_el]))

    w = function(w)
    (u, p) = split(w) 
    (v, q) = testfunctions(w)

    # Граничные условия
    bcs = [
        DirichletBC(W.sub(0).sub(1), Constant(0.0), boundaries, 1),  # низ
        DirichletBC(W.sub(0), Constant((0.0, 0.0)), boundaries, 5),  # цилиндр / дуга
        DirichletBC(W.sub(0).sub(1), Constant(0.0), boundaries, 2),  # верх
        DirichletBC(W.sub(0), Constant((1.0, 0.0)), boundaries, 3),  # вход
        DirichletBC(W.sub(1), Constant(0.0), boundaries, 4),         # выход
    ]

    f = Constant((0.0, 0.0))

    # Вариационная форма
    F = (
        inner(dot(u, nabla_grad(u)), v) * dx
        + nu * inner(grad(u), grad(v)) * dx
        - div(v) * p * dx
        - q * div(u) * dx
        - inner(f, v) * dx
    )

    solve(F == 0, w, bcs)

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

    print("omega min/max:",
      omega.vector().min(),
      omega.vector().max())

    # plt.figure()
    # c = plot(omega, title='Omega')  
    # mesh = omega.function_space().mesh()
    # vertex_values = omega.compute_vertex_values(mesh)
    # vertex_coords = mesh.coordinates()
    # x = vertex_coords[:, 0]
    # y = vertex_coords[:, 1]
    # values = vertex_values
    # mpl.rcParams['hatch.color'] = 'red'
    # plt.tricontourf(
    #     x, y, values,
    #     levels=[values.min(), 0],
    #     hatches=['///'],
    #     alpha=0,
    #     colors='none'
    # )
    # plt.colorbar(c)
    
    # Пробные и тестовые функции
    psi = TrialFunction(V_psi)
    v = TestFunction(V_psi)
    
    a = dot(grad(psi), grad(v)) * dx
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
    print("psi min/max:",
      psi_sol.vector().min(),
      psi_sol.vector().max())
    
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

def solve_all():
    output_folder = "results/navier_stokes"
    shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    grid_names = ["20", "d_0.2", "d_0.5", "d_1.0", "d_1.5"]

    nu_values = np.arange(0.01, 0.11, 0.01)
    all_results = {}

    for grid_name in grid_names:
        for nu in nu_values:
            print(f'====Solving: {grid_name}, nu = {nu}====')
            result = solve_problem(grid_name, nu)

            print(f"Circulation Γ = {result['circulation']}")

            grid_folder = os.path.join(output_folder, grid_name)
            os.makedirs(grid_folder, exist_ok=True)

            fig1, ax1 = plt.subplots(figsize=(10, 8))
            plot_velocity(result["velocity"], f'Velocity field (nu = {nu:.2f})')
            velocity_filename = os.path.join(grid_folder, f"velocity_nu_{nu:.2f}.png")
            plt.savefig(velocity_filename, dpi=300, bbox_inches='tight')
            plt.close(fig1)

            psi = compute_streamfunction(result["velocity"], result["boundaries"])

            fig2, ax2 = plt.subplots(figsize=(10, 8))
            plot_streamfunction(psi, title=f'Stream function (nu = {nu:.2f})')
            stream_filename = os.path.join(grid_folder, f"stream_nu_{nu:.2f}.png")
            plt.savefig(stream_filename, dpi=300, bbox_inches='tight')
            plt.close(fig2)

            all_results[f"{grid_name}_{nu:.2f}"] = float(result['circulation'])

    summary_file = os.path.join(output_folder, "results_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

# -----------------------------
# MAIN
# -----------------------------
def main():
    grid_name = sys.argv[1]
    nu = float(sys.argv[2])  # вязкость

    result = solve_problem(grid_name, nu)

    print("\n=== RESULTS ===")
    print("Circulation Γ =", result["circulation"])

    plot_velocity(result["velocity"], f'Velocity field (nu = {nu})')
    psi = compute_streamfunction(result["velocity"], result["boundaries"])
    plot_streamfunction(psi,  title=f'Stream function (nu = {nu})')

    plt.show()

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == '--all':
        solve_all()
    else:
        main()
