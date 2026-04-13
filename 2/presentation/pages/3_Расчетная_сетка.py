import streamlit as st
import sys
from pathlib import Path

from presentation_data import (  # noqa: E402
    build_mesh_figure,
    discover_mesh_cases,
    family_title,
    group_cases,
    scenario_metrics,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
MESH_ROOT = ROOT_DIR / "mesh"


@st.cache_data
def load_cases():
    return discover_mesh_cases(MESH_ROOT)


cases = load_cases()
grouped = group_cases(cases)


def render_metric_blocks(items):
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items):
        column.markdown(f"**{label}**")
        column.markdown(str(value))


def render_meshes():
    st.header("Расчётные сетки")
    available_families = [
        family for family in ["base", "distance", "height"] if grouped[family]
    ]
    if not available_families:
        st.warning("В репозитории не найдены расчётные сетки.")
        return

    selected_family = st.radio(
        "Семейство сценариев",
        available_families,
        horizontal=True,
        format_func=family_title,
    )
    selected_case = st.selectbox(
        "Вариант сетки",
        grouped[selected_family],
        format_func=lambda case: case.label,
    )
    show_nodes = st.checkbox("Показывать узлы сетки", value=False)
    st.pyplot(
        build_mesh_figure(selected_case, show_nodes=show_nodes),
        use_container_width=True,
    )

    st.markdown("**Параметры выбранного сеточного сценария**")
    render_metric_blocks(scenario_metrics(selected_case))


render_meshes()
