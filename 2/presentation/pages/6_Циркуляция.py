from pathlib import Path
import sys

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

MESH_ROOT = ROOT_DIR / "mesh"

from presentation_data import (  # noqa: E402
    build_circulation_chart,
    case_parameter_label,
    discover_mesh_cases,
    group_cases,
)
from solve import solve_problem  # noqa: E402
from solve_non_symmetrical import solve_problem_non_symmetrical  # noqa: E402


@st.cache_data
def load_cases():
    return discover_mesh_cases(MESH_ROOT)


def solve_selected_case(case, degree):
    if case.family == "height":
        return solve_problem_non_symmetrical(case.name, degree)
    return solve_problem(case.name, degree)


def format_scientific(value):
    value = float(value)
    if value == 0.0:
        return "0"
    exponent = f"{value:.2e}".split("e")[1]
    mantissa = value / (10 ** int(exponent))
    return f"{mantissa:.3f} × 10^{int(exponent)}"


def rows_to_table(rows, first_column, include_kappa=False):
    table = []
    for row in rows:
        item = {
            first_column: row["label"],
            "Циркуляция на первом цилиндре Γ₁": format_scientific(row["gamma_1"]),
            "Циркуляция на втором цилиндре Γ₂": format_scientific(row["gamma_2"]),
            "Различие |Γ₁ - Γ₂|": format_scientific(
                abs(row["gamma_1"] - row["gamma_2"])
            ),
        }
        if include_kappa:
            item["Коэффициент κ₁"] = format_scientific(row["kappa1"])
            item["Коэффициент κ₂"] = format_scientific(row["kappa2"])
        table.append(item)
    return table


def render_results_table(rows, first_column, include_kappa=False):
    st.table(rows_to_table(rows, first_column, include_kappa=include_kappa))


cases = load_cases()
grouped = group_cases(cases)


def render_comparison_slide():
    st.header("Сравнение результатов и циркуляция")
    mode = st.selectbox(
        "Что сравниваем",
        [
            "Степень аппроксимации p",
            "Симметричный случай при фиксированном p",
            "Несимметричный случай при фиксированном p",
        ],
    )

    if mode == "Степень аппроксимации p":
        cases_for_degree = grouped["distance"] + grouped["height"]
        if not cases_for_degree:
            st.info("Нет расчетных вариантов для сравнения по степени аппроксимации.")
            return

        selected_case = st.selectbox(
            "Положение второго цилиндра",
            cases_for_degree,
            format_func=case_parameter_label,
        )
        rows = []
        try:
            with st.spinner("Выполняется серия расчётов по p..."):
                for degree in [1, 2, 3]:
                    result = solve_selected_case(selected_case, degree)
                    rows.append(
                        {
                            "label": f"p = {degree}",
                            "degree": degree,
                            "gamma_1": float(result["gamma1"]),
                            "gamma_2": float(result["gamma2"]),
                            "kappa1": float(result["kappa1"])
                            if "kappa1" in result
                            else None,
                            "kappa2": float(result["kappa2"])
                            if "kappa2" in result
                            else None,
                        }
                    )
        except Exception as exc:
            st.warning(f"Не удалось выполнить серию расчётов: {exc}")
            return

        render_results_table(rows, "Степень аппроксимации")
        st.pyplot(
            build_circulation_chart(
                rows,
                [row["label"] for row in rows],
                "Изменение циркуляций при варьировании p",
            ),
            use_container_width=True,
        )
        return

    degree = st.select_slider(
        "Степень полинома p", options=[1, 2, 3], value=2, key="comparison_degree"
    )

    if mode == "Симметричный случай при фиксированном p":
        target_cases = grouped["distance"]
        chart_title = f"Циркуляции в симметричном случае при p = {degree}"
        include_kappa = False
    else:
        target_cases = grouped["height"]
        chart_title = f"Циркуляции в несимметричном случае при p = {degree}"
        include_kappa = True

    if not target_cases:
        st.info("Для выбранного класса расчетных вариантов недостаточно данных.")
        return

    rows = []
    try:
        with st.spinner("Выполняется серия расчётов..."):
            for case in target_cases:
                result = solve_selected_case(case, degree)
                rows.append(
                    {
                        "label": case_parameter_label(case),
                        "degree": degree,
                        "gamma_1": float(result["gamma1"]),
                        "gamma_2": float(result["gamma2"]),
                        "kappa1": float(result["kappa1"])
                        if "kappa1" in result
                        else None,
                        "kappa2": float(result["kappa2"])
                        if "kappa2" in result
                        else None,
                    }
                )
    except Exception as exc:
        st.warning(f"Не удалось выполнить серию расчётов: {exc}")
        return

    render_results_table(
        rows, "Положение второго цилиндра", include_kappa=include_kappa
    )
    st.pyplot(
        build_circulation_chart(rows, [row["label"] for row in rows], chart_title),
        use_container_width=True,
    )


render_comparison_slide()
