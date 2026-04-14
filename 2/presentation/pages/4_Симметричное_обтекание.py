import streamlit as st
from presentation_data import (  # noqa: E402
    build_solution_figure,
    group_cases,
    discover_mesh_cases,
)
from solve import solve_problem  # noqa: E402
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
MESH_ROOT = ROOT_DIR / "mesh"


@st.cache_data
def load_cases():
    return discover_mesh_cases(MESH_ROOT)


cases = load_cases()
grouped = group_cases(cases)


def format_scientific(value):
    value = float(value)
    if value == 0.0:
        return "0"
    exponent = f"{value:.2e}".split("e")[1]
    mantissa = value / (10 ** int(exponent))
    return f"{mantissa:.3f} × 10^{int(exponent)}"


def render_metric_blocks(items):
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items):
        column.markdown(f"**{label}**")
        column.markdown(str(value))


menu = st.sidebar.radio(
    "***",
    (
        "Фрагмент кода",
        "Визуализации решения",
    ),
)

if menu == "Фрагмент кода":
    r"""
    
    **Симметричный решатель**
    
    """
    code = """     
    # Загрузка сетки и разметки границ
    mesh = Mesh(f"mesh/{directory}/{prefix}.xml")
    boundaries = MeshFunction(
        "size_t", mesh, f"mesh/{directory}/{prefix}_facet_region.xml"
    )
    
    # Интегрирование по частям границы
    ds = Measure("ds", subdomain_data=boundaries)
    
    # Функциональное пространство
    V = FunctionSpace(mesh, "CG", degree)
    
    # Условие на входе в канал
    u_1 = Expression("x[1]", degree=degree)
    
    # Граничные условия
    bcs = [
        DirichletBC(V, Constant(0.0), boundaries, 1),  # нижняя граница
        DirichletBC(V, Constant(1.0), boundaries, 2),  # верхняя граница
        DirichletBC(V, Constant(0.5), boundaries, 5),  # цилиндр 1
        DirichletBC(V, Constant(0.5), boundaries, 6),  # цилиндр 2
        DirichletBC(V, u_1, boundaries, 3),            # вход
    ]
    
    # Вариационная задача
    u = TrialFunction(V)
    v = TestFunction(V)
    f = Constant(0.0)
    a = dot(grad(u), grad(v)) * dx
    L = f * v * dx
    
    # Решение задачи
    solution = Function(V)
    solve(a == L, solution, bcs)
    
    # Вычисление циркуляции на цилиндрах
    n = FacetNormal(mesh)
    u_n = dot(grad(solution), n)
    Gamma1 = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=5))
    Gamma2 = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=6))
    """
    st.code(code, language="python")

if menu == "Визуализации решения":
    st.header("Визуализации решения")
    available_cases = grouped["distance"]

    degree = st.select_slider("Степень полинома p", options=[1, 2, 3], value=2)
    selected_case = st.selectbox(
        "Сценарий", available_cases, format_func=lambda case: case.label
    )

    try:
        with st.spinner("Выполняется расчёт..."):
            result = solve_problem(selected_case.name, degree)
    except Exception as exc:
        st.warning(f"Не удалось выполнить расчёт: {exc}")

    st.pyplot(
        build_solution_figure(result["solution"], degree), use_container_width=True
    )

    items = [
        (r"$I_1$", format_scientific(result["gamma1"])),
        (r"$I_2$", format_scientific(result["gamma2"])),
    ]
    render_metric_blocks(items)

    st.markdown(
        r"""
        Здесь
        $$
        I_1 = \oint_{\gamma_1} \frac{\partial \psi}{\partial n}\, dx, \quad
        I_2 = \oint_{\gamma_2} \frac{\partial \psi}{\partial n}\, dx
        $$
        используются как интегральные характеристики по границам цилиндров.
        """
    )
