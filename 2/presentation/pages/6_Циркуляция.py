from pathlib import Path
import sys

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

MESH_ROOT = ROOT_DIR / "mesh"

from presentation_data import (  # noqa: E402
    build_circulation_chart,
    discover_mesh_cases,
    family_title,
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


def rows_to_table(rows, first_column, include_degree=False, include_kappa=False):
    table = []
    for row in rows:
        item = {
            first_column: row["label"],
            r"$\Gamma_1$": format_scientific(row["gamma_1"]),
            r"$\Gamma_2$": format_scientific(row["gamma_2"]),
            r"$|\Gamma_1 - \Gamma_2|$": format_scientific(
                abs(row["gamma_1"] - row["gamma_2"])
            ),
        }
        if include_kappa:
            item["kappa_1"] = format_scientific(row["kappa1"])
            item["kappa_2"] = format_scientific(row["kappa2"])
        table.append(item)
    return table


cases = load_cases()
grouped = group_cases(cases)


def render_comparison_slide():
    st.header("Сравнение результатов и циркуляция")
    mode = st.selectbox(
        "Режим сравнения",
        [
            "По степени p для выбранного сценария",
            "Симметричные сценарии при фиксированном p",
            "Несимметричные сценарии при фиксированном p",
        ],
    )

    if mode == "По степени p для выбранного сценария":
        cases_for_degree = grouped["distance"] + grouped["height"]
        if not cases_for_degree:
            st.info("Нет сценариев для сравнения по степени аппроксимации.")
            return

        selected_case = st.selectbox(
            "Сценарий для сравнения по p",
            cases_for_degree,
            format_func=lambda case: f"{family_title(case.family)} | {case.label}",
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

        st.dataframe(
            rows_to_table(rows, "Вариант", include_degree=True),
            use_container_width=True,
        )
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

    if mode == "Симметричные сценарии при фиксированном p":
        target_cases = grouped["distance"]
        first_column = "Симметричный сценарий"
        chart_title = f"Циркуляции в симметричных сценариях при p = {degree}"
        include_kappa = False
    else:
        target_cases = grouped["height"]
        first_column = "Несимметричный сценарий"
        chart_title = f"Циркуляции в несимметричных сценариях при p = {degree}"
        include_kappa = True

    if not target_cases:
        st.info("Для выбранного класса сценариев в репозитории недостаточно данных.")
        return

    rows = []
    try:
        with st.spinner("Выполняется серия расчётов по сценариям..."):
            for case in target_cases:
                result = solve_selected_case(case, degree)
                rows.append(
                    {
                        "label": case.label,
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

    st.dataframe(
        rows_to_table(
            rows, first_column, include_degree=False, include_kappa=include_kappa
        ),
        use_container_width=True,
    )
    st.pyplot(
        build_circulation_chart(rows, [row["label"] for row in rows], chart_title),
        use_container_width=True,
    )


render_comparison_slide()
