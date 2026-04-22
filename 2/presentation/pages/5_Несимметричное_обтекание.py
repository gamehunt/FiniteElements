import streamlit as st
from presentation_data import (  # noqa: E402
    build_solution_figure,
    case_parameter_value,
    discover_mesh_cases,
    group_cases,
)
from solve_non_symmetrical import solve_problem_non_symmetrical  # noqa: E402
from pathlib import Path
import sys

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
    
    **Несимметричный решатель**
    
    """
    code = """     
    # Загрузка сетки и разметки границ
    mesh = Mesh(f"mesh/{directory}/{prefix}.xml")
    boundaries = MeshFunction(
        "size_t", mesh, f"mesh/{directory}/{prefix}_facet_region.xml"
    )
    
    # Интегрирование по частям границы
    ds = Measure("ds", subdomain_data=boundaries)
    
    # Внешняя нормаль к границе
    n = FacetNormal(mesh)
    
    # Функциональное пространство
    V = FunctionSpace(mesh, "CG", degree)
    
    # Условие на входе в канал
    u_1 = Expression("x[1]", degree=degree)
    
    # Вариационная задача
    u = TrialFunction(V)
    v = TestFunction(V)
    f = Constant(0.0)
    a = dot(grad(u), grad(v)) * dx
    L = f * v * dx
    
    # Основное решение u0
    bcs0 = [
        DirichletBC(V, Constant(0.0), boundaries, 1),  # нижняя граница
        DirichletBC(V, Constant(1.0), boundaries, 2),  # верхняя граница
        DirichletBC(V, Constant(0.0), boundaries, 5),  # цилиндр 1
        DirichletBC(V, Constant(0.0), boundaries, 6),  # цилиндр 2
        DirichletBC(V, u_1, boundaries, 3),            # вход
    ]
    u0 = Function(V)
    solve(a == L, u0, bcs0)
    
    # Вспомогательное решение u1
    # На первом цилиндре задаем единичное значение
    bcs1 = [
        DirichletBC(V, Constant(0.0), boundaries, 1),
        DirichletBC(V, Constant(0.0), boundaries, 2),
        DirichletBC(V, Constant(1.0), boundaries, 5),  # цилиндр 1
        DirichletBC(V, Constant(0.0), boundaries, 6),  # цилиндр 2
        DirichletBC(V, Constant(0.0), boundaries, 3),
    ]
    u1 = Function(V)
    solve(a == L, u1, bcs1)
    
    # Вспомогательное решение u2
    # На втором цилиндре задаем единичное значение
    bcs2 = [
        DirichletBC(V, Constant(0.0), boundaries, 1),
        DirichletBC(V, Constant(0.0), boundaries, 2),
        DirichletBC(V, Constant(0.0), boundaries, 5),
        DirichletBC(V, Constant(1.0), boundaries, 6),  # цилиндр 2
        DirichletBC(V, Constant(0.0), boundaries, 3),
    ]
    u2 = Function(V)
    solve(a == L, u2, bcs2)
    
    # Потоки через границы цилиндров
    flux0 = dot(grad(u0), n)
    flux1 = dot(grad(u1), n)
    flux2 = dot(grad(u2), n)
    
    # Интегральные характеристики для двух цилиндров
    c01 = assemble(flux0 * ds(5))
    c11 = assemble(flux1 * ds(5))
    c21 = assemble(flux2 * ds(5))
    
    c02 = assemble(flux0 * ds(6))
    c12 = assemble(flux1 * ds(6))
    c22 = assemble(flux2 * ds(6))
    
    # Система на коэффициенты kappa1, kappa2
    A = np.array([
        [c11, c21],
        [c12, c22]
    ])
    b = -np.array([c01, c02])
    
    kappa = np.linalg.solve(A, b)
    k1, k2 = kappa
    
    # Итоговое решение как линейная комбинация
    u_final = Function(V)
    u_final.vector()[:] = (
        u0.vector()
        + k1 * u1.vector()
        + k2 * u2.vector()
    )
    
    # Проверка циркуляции на цилиндрах
    flux_final = dot(grad(u_final), n)
    Gamma1 = assemble(flux_final * ds(5))
    Gamma2 = assemble(flux_final * ds(6))
    """
    st.code(code, language="python")

if menu == "Визуализации решения":
    st.header("Визуализации решения")
    available_cases = grouped["height"]

    degree = st.select_slider("Степень полинома p", options=[1, 2, 3], value=2)
    selected_case = st.selectbox(
        "Параметр h₂", available_cases, format_func=case_parameter_value
    )

    try:
        with st.spinner("Выполняется расчёт..."):
            result = solve_problem_non_symmetrical(selected_case.name, degree)
    except Exception as exc:
        st.warning(f"Не удалось выполнить расчёт: {exc}")

    st.pyplot(
        build_solution_figure(result["solution"], degree), use_container_width=True
    )

    items = [
        (r"$\Gamma_1$", format_scientific(result["gamma1"])),
        (r"$\Gamma_2$", format_scientific(result["gamma2"])),
    ]
    items.extend(
        [
            (r"$\kappa_1$", format_scientific(result["kappa1"])),
            (r"$\kappa_2$", format_scientific(result["kappa2"])),
        ]
    )
    render_metric_blocks(items)
