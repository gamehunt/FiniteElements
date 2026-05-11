import streamlit as st
import numpy as np
from pathlib import Path
import json

def find_project_root():
    current = Path(__file__).resolve()

    for parent in [current.parent, *current.parents]:
        if (parent / "grids").exists():
            return parent

    raise RuntimeError("Не удалось найти корень проекта: папка grids/ не найдена.")


PROJECT_ROOT = find_project_root()
GRIDS_ROOT = PROJECT_ROOT / "grids"
RESULTS_ROOT = PROJECT_ROOT / "results/navier_stokes"

def discover_grids():
    cases = []

    for directory in sorted(p for p in GRIDS_ROOT.iterdir() if p.is_dir()):
        name = directory.name
        prefix = f"grid_{name}"

        xml_path = directory / f"{prefix}.xml"

        if not xml_path.exists():
            continue

        if name.startswith("cyl_d_"):
            continue
            #label = f"Цилиндр D = {name.replace('cyl_d_', '')}"
            #family = "cylinder"
        elif name.isdigit():
            if int(name) < 20:
                continue
            label = f"N = {name}"
            family = "semicylinder"
        elif name.startswith("d_"):
            label = f"Полуцилиндр D = {name.replace('d_', '')}"
            family = "semicylinder_diameter"
        else:
            label = f"Сетка {name}"
            family = "other"

        cases.append(
            {
                "name": name,
                "label": label,
                "family": family,
            }
        )

    def sort_key(case):
        name = case["name"]

        if name.isdigit():
            return (0, float(name))

        if name.startswith("d_"):
            return (1, float(name.replace("d_", "")))

        if name.startswith("cyl_d_"):
            return (2, float(name.replace("cyl_d_", "")))

        return (3, name)

    return sorted(cases, key=sort_key)


menu = st.sidebar.radio(
    "***",
    (
        "Уравнения Навье-Стокса",
        "Результаты расчетов",
        "Программная реализация",
    ),
)

if menu == "Уравнения Навье-Стокса":
    st.markdown(r"""
    ### Уравнения Навье-Стокса для несжимаемой жидкости

    **Стационарная форма** ($\partial / \partial t = 0$):
    $$
    (\mathbf{u} \cdot \nabla) \mathbf{u} = -\frac{1}{\rho} \nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{f}
    $$

    **Вариационная постановка**:
    $$
    V_0 = \{ \mathbf{v} \in [H^1(\Omega)]^2 : \mathbf{v}(x) = 0, \ x \in \partial \Omega \}
    $$

    $$
    Q = \{ q \in [H^1(\Omega)] : q(x) = 0, \ x \in \partial \Omega \}
    $$

    $$
    (\mathbf{u} \cdot \nabla \mathbf{u}, \mathbf{v})
    + \nu (\nabla \mathbf{u}, \nabla \mathbf{v})
    - (p, \nabla \cdot \mathbf{v})
    - (q, \nabla \cdot \mathbf{u})
    - (\mathbf{f}, \mathbf{v})
    = 0
    $$

    $$
    \forall (\mathbf{v}, q) \in V_0 \times Q
    $$

    **Уравнение неразрывности** (сохранение массы):
    $$
    \nabla \cdot \mathbf{u} = 0
    $$

    **В терминах функции тока** (2D):

    - Функция тока: $u = \frac{\partial \psi}{\partial y},\quad v = -\frac{\partial \psi}{\partial x}$
    - Уравнение Пуассона для $\psi$: $\nabla^2 \psi = -\omega$

    **Ключевые параметры**:
    - $\nu$ - кинематическая вязкость
    - Число Рейнольдса: $Re = \frac{UL}{\nu}$
    """)

if menu == "Результаты расчетов":
    st.markdown("## Результаты расчетов")


    nu_list = np.arange(0.01, 0.11, 0.01)
    nu_selected = st.select_slider(
        "Кинематическая вязкость ν",
        options=nu_list,
        format_func=lambda x: f"{x:.2f}",
        value=0.05
    )

    cases = discover_grids()

    if not cases:
        st.warning(f"Сетки не найдены в папке `{GRIDS_ROOT}`.")
        st.stop()

    case = st.selectbox(
        "Выбор расчетной сетки",
        cases,
        format_func=lambda c: c["label"],
    )

    with open(RESULTS_ROOT / "results_summary.json", 'r') as f:
        gamma_data = json.load(f)

    st.markdown(f"**Параметры:** ν = {nu_selected:.2f}, сетка = {case['label']}")
    s = gamma_data[f"{case['name']}_{nu_selected:.2f}"]
    st.markdown(f"**Циркуляция  $\\Gamma$:** {s:.4f}")

    nu_str = f"{nu_selected:.2f}"
    stream_path = RESULTS_ROOT / f"{case['name']}/stream_nu_{nu_str}.png"
    vel_path = RESULTS_ROOT / f"{case['name']}/velocity_nu_{nu_str}.png"

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Функция тока**")
    with col2:
        st.markdown("**Поле скорости**")

    col1, col2 = st.columns(2, vertical_alignment='center')

    with col1:
        try:
            st.image(stream_path, use_container_width=True)
        except FileNotFoundError:
            st.warning(f"Изображение не найдено: {stream_path}")

    with col2:
        try:
            st.image(vel_path, use_container_width=True)
        except FileNotFoundError:
            st.warning(f"Изображение не найдено: {vel_path}")

if menu == "Программная реализация":
    st.markdown("## Программная реализация решателя")

    st.markdown("""
    - **Taylor-Hood элементы** (P2-P1) - квадратичная аппроксимация скорости, линейная - давления
    - В качестве нелинейного решателя используется метод Ньютона, реализованный в FEniCS
    """)

    st.markdown("### Основные компоненты решателя")

    st.markdown("""
    **Решение уравнений Навье-Стокса**:
    """)
    st.code("""
def solve_navier_stokes(mesh, boundaries, nu=0.01):
    # Taylor–Hood (P2-P1)
    V_el = VectorElement("CG", mesh.ufl_cell(), 2)  # Скорость (квадратичная)
    Q_el = FiniteElement("CG", mesh.ufl_cell(), 1)  # Давление (линейная)
    W = FunctionSpace(mesh, MixedElement([V_el, Q_el]))

    w = function(w)
    (u, p) = split(w) 
    (v, q) = testfunctions(w)

    # Граничные условия
    bcs = [
        # Низ (boundary 1): скольжение по y
        DirichletBC(W.sub(0).sub(1), Constant(0.0), boundaries, 1),
    
        # Верх (boundary 2): скольжение по y  
        DirichletBC(W.sub(0).sub(1), Constant(0.0), boundaries, 2),
    
        # Вход (boundary 3): заданный профиль скорости
        DirichletBC(W.sub(0), Constant((1.0, 0.0)), boundaries, 3),
    
        # Выход (boundary 4): нулевое давление
        DirichletBC(W.sub(1), Constant(0.0), boundaries, 4),
    
        # Цилиндр (boundary 5): прилипание
        DirichletBC(W.sub(0), Constant((0.0, 0.0)), boundaries, 5),
    ]

    f = Constant((0.0, 0.0))

    # Вариационная форма
    F = (inner(dot(u_k, nabla_grad(u)), v) * dx      # конвекция
         + nu * inner(grad(u), grad(v)) * dx         # диффузия
         - div(v) * p * dx                           # градиент давления
         - q * div(u) * dx                           # неразрывность
         - inner(f, v) * dx)                         # внешняя сила

    solve(F == 0, w, bcs)

    u_sol, p_sol = w.split()
    return u_sol, p_sol
    """, language="python")

    st.markdown(r"""
    **Вычисление функции тока** - решение уравнения Пуассона:

    $$
        \nabla^2 \psi = -\omega, \quad \omega = \nabla \times \mathbf{u}
    $$
    """)
    st.code("""
    def compute_streamfunction(u, boundaries):
        # Пространство для функции тока
        V_psi = FunctionSpace(mesh, "CG", 2)
    
        # Завихренность из поля скорости
        omega = project(curl(u), V_psi)
    
        # Слабая форма уравнения Пуассона
        psi = TrialFunction(V_psi)
        v = TestFunction(V_psi)
    
        a = dot(grad(psi), grad(v)) * dx
        L = omega * v * dx
    
        # Решение
        psi_sol = Function(V_psi)
        solve(a == L, psi_sol, bc_psi)
    
        return psi_sol
    """, language="python")

    st.caption("""
    Функция тока позволяет визуализировать линии тока жидкости.
    """)

    st.divider()
