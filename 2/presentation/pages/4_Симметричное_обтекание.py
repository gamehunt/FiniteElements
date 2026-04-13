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

st.pyplot(build_solution_figure(result["solution"], degree), use_container_width=True)

items = [
    (r"$I_1$", format_scientific(result["gamma1"])),
    (r"$I_2$", format_scientific(result["gamma2"])),
]
render_metric_blocks(items)

st.markdown(
    r"""
    Здесь
    $$
    I_1 = \int_{\partial D_1} \partial_n \psi \, ds, \qquad
    I_2 = \int_{\partial D_2} \partial_n \psi \, ds
    $$
    используются как интегральные характеристики по границам цилиндров.
    """
)
