from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def find_project_root():
    current = Path(__file__).resolve()

    for parent in [current.parent, *current.parents]:
        if (parent / "results").exists() and (parent / "grids").exists():
            return parent

    raise RuntimeError(
        "Не удалось найти корень проекта: папки results/ и grids/ не найдены."
    )


PROJECT_ROOT = find_project_root()

RESULTS_REFINEMENT_ROOT = PROJECT_ROOT / "results" / "one_vortex_refinement"
RESULTS_COMMON_ROOT = PROJECT_ROOT / "results" / "one_vortex"

DEGREES = [1, 2, 3]
GAMMAS = [-1.0, -2.5, -5.0]
REFINEMENT_GRIDS = ["5", "10", "20"]

def gamma_dir_name(gamma):
    return f"gamma_{gamma:g}"

def degree_dir_name(degree):
    return f"degree_{degree}"

def grid_to_diameter(grid_name):
    if grid_name.startswith("d_"):
        try:
            return float(grid_name.replace("d_", ""))
        except ValueError:
            return None

    return None


def format_diameter_grid(grid_name):
    diameter = grid_to_diameter(grid_name)

    if diameter is None:
        return grid_name

    return f"D = {diameter:g}"


def discover_diameter_grids():
    if not RESULTS_COMMON_ROOT.exists():
        return []

    grids = [
        path.name
        for path in RESULTS_COMMON_ROOT.iterdir()
        if path.is_dir() and path.name.startswith("d_")
    ]

    def sort_key(name):
        diameter = grid_to_diameter(name)

        if diameter is None:
            return -1.0

        return diameter

    return sorted(grids, key=sort_key, reverse=True)

def result_dir(root, grid_name, gamma, degree):
    return root / grid_name / gamma_dir_name(gamma) / degree_dir_name(degree)

def read_summary(root, grid_name, gamma, degree):
    path = result_dir(root, grid_name, gamma, degree) / "summary.csv"

    if not path.exists():
        return None

    return pd.read_csv(path)


def read_history(root, grid_name, gamma, degree):
    path = result_dir(root, grid_name, gamma, degree) / "history.csv"

    if not path.exists():
        return None

    return pd.read_csv(path)


def image_path(root, grid_name, gamma, degree, filename):
    return result_dir(root, grid_name, gamma, degree) / filename


def format_value(value, digits=4):
    if value is None:
        return "—"

    try:
        if pd.isna(value):
            return "—"
    except TypeError:
        pass

    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)

    if abs(value) >= 1e4 or (abs(value) < 1e-3 and value != 0):
        return f"{value:.{digits}e}"

    return f"{value:.{digits}g}"


def render_table(headers, rows, widths):
    header_cols = st.columns(widths)

    for col, header in zip(header_cols, headers):
        with col:
            st.markdown(f"**{header}**")

    for row in rows:
        cols = st.columns(widths)

        for col, value in zip(cols, row):
            with col:
                st.markdown(
                    f"""
                    <div style="
                        padding: 0.45rem 0;
                        border-bottom: 1px solid rgba(128,128,128,0.25);
                        font-size: 1.02rem;
                    ">
                        {value}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

def build_refinement_summary(degree, gamma=-1):
    rows = []

    for grid_name in REFINEMENT_GRIDS:
        summary = read_summary(RESULTS_REFINEMENT_ROOT, grid_name, gamma, degree)

        if summary is None or summary.empty:
            continue

        row = summary.iloc[0].to_dict()

        rows.append(
            {
                "N": grid_name,
                "N_v": row.get("vertices"),
                "N_T": row.get("cells"),
                "N_h": row.get("dofs"),
                "N_iter": row.get("iterations"),
                "eps_final": row.get("error_final"),
                "final_residual": row.get("final_residual"),
                "psi_min": row.get("psi_min"),
                "S_final": row.get("vortex_area"),
                "omega_final": row.get("omega_value"),
                "gamma_num": row.get("circulation"),
            }
        )

    return pd.DataFrame(rows)

def build_gamma_summary(degree):
    rows = []

    for gamma in GAMMAS:
        summary = read_summary(RESULTS_COMMON_ROOT, "20", gamma, degree)

        if summary is None or summary.empty:
            continue

        row = summary.iloc[0].to_dict()

        rows.append(
            {
                "gamma": gamma,
                "N_v": row.get("vertices"),
                "N_T": row.get("cells"),
                "N_h": row.get("dofs"),
                "N_iter": row.get("iterations"),
                "eps_final": row.get("error_final"),
                "psi_min": row.get("psi_min"),
                "S_final": row.get("vortex_area"),
                "omega_final": row.get("omega_value")
            }
        )

    return pd.DataFrame(rows)

def render_gamma_summary_table(summary_table):
    headers = [
        r"Г",
        # r"Вершины",
        # r"Треугольники",
        r"$N_{\mathrm{iter}}$",
        r"$\psi_{min}$",
        r"$S_{\mathrm{final}}$",
        r"$\omega_{\mathrm{final}}$",
    ]

    widths = [0.7, 
              # 1.4, 
              # 1.8, 
              1.2, 
              # 1.5, 
              1.4, 
              1.4, 
              1.4]

    rows = []
    for _, row in summary_table.iterrows():
        print(row)
        rows.append(
            [
                row["gamma"],
                # int(row["N_v"]),
                # int(row["N_T"]),
                # int(row["N_h"]),
                int(row["N_iter"]),
                # format_value(row["eps_final"]),
                format_value(row["psi_min"]),
                format_value(row["S_final"]),
                format_value(row["omega_final"]),
                # format_value(row["gamma_num"]),
            ]
        )

    render_table(headers, rows, widths)

def build_diameter_summary(grids, gamma, degree):
    rows = []

    for grid_name in grids:
        summary = read_summary(RESULTS_COMMON_ROOT, grid_name, gamma, degree)
        print(grid_name, gamma, degree, summary)

        if summary is None or summary.empty:
            continue

        row = summary.iloc[0].to_dict()
        diameter = grid_to_diameter(grid_name)

        rows.append(
            {
                "D": diameter,
                "grid": grid_name,
                "N_v": row.get("vertices"),
                "N_T": row.get("cells"),
                "N_h": row.get("dofs"),
                "N_iter": row.get("iterations"),
                "psi_min": row.get("psi_min"),
                "eps_final": row.get("error_final"),
                "S_final": row.get("vortex_area"),
                "omega_final": row.get("omega_value"),
                "gamma_num": row.get("circulation"),
            }
        )

    return pd.DataFrame(rows)


def render_refinement_summary_table(summary_table):
    headers = [
        r"$N$",
        r"Вершины",
        r"Треугольники",
        r"$N_{\mathrm{iter}}$",
        # r"$\varepsilon_{\mathrm{final}}$",
        r"$R$",
        r"$\psi_{min}$",
        r"$S_{\mathrm{final}}$",
        r"$\omega_{\mathrm{final}}$",
    ]

    widths = [0.7, 
              1.4, 
              1.8, 
              1.2, 
              1.2, 
              # 1.5, 
              1.4, 
              1.4, 
              1.4]

    rows = []
    for _, row in summary_table.iterrows():
        print(row)
        rows.append(
            [
                row["N"],
                int(row["N_v"]),
                int(row["N_T"]),
                # int(row["N_h"]),
                int(row["N_iter"]),
                # format_value(row["eps_final"]),
                format_value(row["final_residual"]),
                format_value(row["psi_min"]),
                format_value(row["S_final"]),
                format_value(row["omega_final"]),
                # format_value(row["gamma_num"]),
            ]
        )

    render_table(headers, rows, widths)


def render_diameter_summary_table(summary_table):
    headers = [
        r"$D$",
        r"Вершины",
        r"Треугольники",
        # r"$N_h$",
        r"$N_{\mathrm{iter}}$",
        r"$\psi_{min}$",
        # r"$\varepsilon_{\mathrm{final}}$",
        r"$S_{\mathrm{final}}$",
        r"$\omega_{\mathrm{final}}$",
        # r"$\Gamma_{\mathrm{control}}$",
    ]

    widths = [
            0.7, 
            1.1, 
            1.5, 
            # 1.1,
            1.2, 
            1.5, 
            # 1.4, 
            1.4, 
            1.4
            ]

    rows = []

    for _, row in summary_table.iterrows():
        rows.append(
            [
                format_value(row["D"]),
                int(row["N_v"]),
                int(row["N_T"]),
                # int(row["N_h"]),
                int(row["N_iter"]),
                # format_value(row["error_final"]),
                format_value(row["psi_min"]),
                format_value(row["S_final"]),
                format_value(row["omega_final"]),
                # format_value(row["gamma_num"]),
            ]
        )

    render_table(headers, rows, widths)


def build_refinement_history(degree,gamma=-1):
    frames = []

    for grid_name in REFINEMENT_GRIDS:
        history = read_history(RESULTS_REFINEMENT_ROOT, grid_name, gamma, degree)

        if history is None or history.empty:
            continue

        history = history.copy()
        history["group"] = f"N = {grid_name}"
        history["group_order"] = float(grid_name)
        frames.append(history)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)

def build_diameter_degree_history(grid_name, gamma):
    frames = []

    for degree in DEGREES:
        history = read_history(RESULTS_COMMON_ROOT, grid_name, gamma, degree)

        if history is None or history.empty:
            continue

        history = history.copy()
        history["group"] = f"p = {degree}"
        history["group_order"] = degree
        frames.append(history)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)

def plot_history_comparison(history, value_column, title, y_title, value_title):
    fig = go.Figure()

    if history.empty or value_column not in history.columns:
        return fig

    groups = (
        history[["group", "group_order"]]
        .drop_duplicates()
        .sort_values("group_order", ascending=False)
    )

    for _, group_row in groups.iterrows():
        group_name = group_row["group"]
        part = history[history["group"] == group_name].copy()

        fig.add_trace(
            go.Scatter(
                x=part["iteration"],
                y=part[value_column],
                mode="lines+markers",
                name=group_name,
                hovertemplate=(
                    f"<b>{group_name}</b><br>"
                    "Итерация: %{x}<br>"
                    f"{value_title}: " + "%{y:.6g}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Итерация",
        yaxis_title=y_title,
        hovermode="x unified",
        hoverdistance=-1,
        spikedistance=-1,
        height=430,
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title="Вариант",
    )

    fig.update_xaxes(
        showspikes=True,
        spikecolor="gray",
        spikethickness=1,
        spikedash="dot",
        spikemode="across",
        spikesnap="cursor",
    )

    return fig


def render_image(root, grid_name, gamma, degree, filename, title_func):
    if title_func:
        st.markdown(f"### {title_func(grid_name)}")
    
    path = image_path(root, grid_name, gamma, degree, filename)
    
    if path.exists():
        st.image(str(path), use_container_width=True)
    else:
        st.warning(f"Нет файла `{path}`")


def render_verification():
    st.title("Верификация")

    col1, col2 = st.columns([1, 1])

    with col1:
        degree = st.select_slider(
            "Степень полинома p",
            options=DEGREES,
            value=2,
            format_func=lambda x: f"p = {x}",
        )

    with col2:
        grid = st.selectbox(
            "Выбор расчетной сетки",
            REFINEMENT_GRIDS,
            format_func=lambda x: f"N = {x}",
        )


    st.subheader("Функция тока")
    render_image(
        root=RESULTS_REFINEMENT_ROOT,
        grid_name=grid,
        gamma=-1,
        degree=degree,
        filename="psi.png",
        title_func=None,
    )

    st.subheader("Сводные данные")
    summary_table = build_refinement_summary(degree)
    if summary_table.empty:
        st.warning(
            f"Нет результатов в папке `{RESULTS_REFINEMENT_ROOT}` для выбранных параметров."
        )
        st.stop()

    render_refinement_summary_table(summary_table)
    history = build_refinement_history(degree)
    if history.empty:
        st.warning("Нет history.csv для выбранных параметров.")
        st.stop()

    render_history_graphs(history)

def render_gamma_results():
    st.title("Зависимость от разных Г")

    col1, col2 = st.columns([1, 1])

    with col1:
        degree = st.select_slider(
            "Степень полинома p",
            options=DEGREES,
            value=2,
            format_func=lambda x: f"p = {x}",
        )

    with col2:
        gamma = st.select_slider(
            "Циркуляция",
            options=GAMMAS,
            value=GAMMAS[0],
            format_func=lambda x: f"Г = {x}",
        )


    st.subheader("Функция тока")
    render_image(
        root=RESULTS_COMMON_ROOT,
        grid_name="20",
        gamma=gamma,
        degree=degree,
        filename="psi.png",
        title_func=None,
    )

    st.subheader("Сводные данные")
    summary_table = build_gamma_summary(degree)
    if summary_table.empty:
        st.warning(
            f"Нет результатов в папке `{RESULTS_REFINEMENT_ROOT}` для выбранных параметров."
        )
        st.stop()

    render_gamma_summary_table(summary_table)
    # history = build_refinement_history(degree, gamma)
    # if history.empty:
    #     st.warning("Нет history.csv для выбранных параметров.")
    #     st.stop()
    #
    # render_history_graphs(history)

def render_diameter_results():
    st.title("Зависимость от диаметра цилиндра")

    grids = discover_diameter_grids()

    if not grids:
        st.warning(
            f"Результаты по диаметрам не найдены в папке `{RESULTS_COMMON_ROOT}`."
        )
        st.stop()

    col3, col1, col2 = st.columns([1, 1, 1])

    with col3:    
        degree = st.select_slider(
            "Степень полинома p",
            options=DEGREES,
            value=2,
            format_func=lambda x: f"p = {x}",
        )

    with col2:
        grid_name = st.selectbox(
            "Диаметр полуцилиндра",
            grids,
            format_func=format_diameter_grid,
        )

    with col1:
        gamma = st.select_slider(
            "Циркуляция Γ",
            options=GAMMAS,
            value=GAMMAS[0],
            format_func=lambda x: f"Γ = {x:g}",
            key="diameter_gamma",
        )


    st.subheader("Функция тока")
    render_image(
        root=RESULTS_COMMON_ROOT,
        grid_name=grid_name,
        gamma=gamma,
        degree=degree,
        filename="psi.png",
        title_func=None
    )

    st.subheader("Сводные данные")
    summary_table = build_diameter_summary(grids, gamma, degree)
    if summary_table.empty:
        st.warning("Для выбранных параметров нет сохранённых summary.csv.")
        st.stop()
    render_diameter_summary_table(summary_table)

    history = build_diameter_degree_history(grid_name, gamma)
    if history.empty:
        st.warning("Нет history.csv для выбранных параметров.")
        st.stop()

    render_history_graphs(history)

def render_history_graphs(history):
    st.subheader("Сходимость")

    fig = plot_history_comparison(
        history=history,
        value_column="error",
        title="",
        y_title="Ошибка",
        value_title="Ошибка",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Площадь вихревой области")

    fig = plot_history_comparison(
        history=history,
        value_column="vortex_area",
        title="",
        y_title="Площадь",
        value_title="Площадь",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Завихрённость")

    fig = plot_history_comparison(
        history=history,
        value_column="omega_value",
        title="",
        y_title="Завихрённость",
        value_title="ω",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Минимум функции тока")

    fig = plot_history_comparison(
        history=history,
        value_column="psi_min",
        title="",
        y_title="Минимум функции тока",
        value_title="$\psi$",
    )
    st.plotly_chart(fig, use_container_width=True)

def render_solver_code():
    st.title("Код решателя")

    r"""
    Для одиночного вихря используется область с полуцилиндром.
    Неизвестной является функция тока $\psi$.

    На каждой итерации решается задача Пуассона:

    $$
    -\Delta \psi^{k+1} = \omega^k.
    $$

    Сначала решается потенциальная задача без завихрённости:
    """

    st.code(
        """
psi = Function(V)

# Потенциальное решение
solve_poisson(V, bcs, Constant(0.0), psi)
""",
        language="python",
    )

    r"""
    Начальная вихревая зона задаётся прямоугольником за полуцилиндром:

    $$
    D^0 =
    \left\{
    (x_1,x_2):
    l_2 < x_1 < l_2+r_c,\quad
    x_2 < r_c
    \right\}.
    $$
    """

    st.code(
        """
wake_zone = WakeZone(
    l2=l2,
    r_cyl=0.5,
    psi_value=-0.05,
    degree=degree,
)

psi.vector().axpy(1.0, interpolate(wake_zone, V).vector())
""",
        language="python",
    )

    r"""
    На $k$-й итерации вихревая область определяется условием:

    $$
    D^k = \{x:\psi^k(x)<0\}.
    $$

    Её площадь:

    $$
    S^k = |D^k|.
    $$
    """

    st.code(
        """
def compute_vortex_area(psi, mesh, dx):
    V_dg0 = FunctionSpace(mesh, "DG", 0)

    indicator = Function(V_dg0)
    psi_dg0 = interpolate(psi, V_dg0)

    psi_values = psi_dg0.vector().get_local()
    indicator_values = np.where(psi_values < 0, 1.0, 0.0)

    indicator.vector().set_local(indicator_values)
    indicator.vector().apply("insert")

    area = assemble(indicator * dx)

    return area
""",
        language="python",
    )

    r"""
    По заданной циркуляции $\Gamma$ вычисляется постоянная завихрённость
    внутри вихревой области:

    $$
    \omega^k = \frac{\Gamma}{S^k}.
    $$
    """

    st.code(
        """
vortex_area = compute_vortex_area(psi, mesh, dx)

omega_value = gamma / vortex_area

psi_values = psi.vector().get_local()
omega_values = np.where(psi_values < 0, omega_value, 0.0)

omega.vector().set_local(omega_values)
omega.vector().apply("insert")
""",
        language="python",
    )

    r"""
    Затем снова решается задача Пуассона:

    $$
    -\Delta \psi^{k+1} = \omega^k.
    $$

    Критерий остановки:

    $$
    \|\psi^{k+1}-\psi^k\|_{L^2}<\varepsilon.
    $$
    """

    st.code(
        """
psi_new = Function(V)
solve_poisson(V, bcs, omega, psi_new)

error = errornorm(psi_new, psi, "L2")

psi.assign(psi_new)

if error < tol:
    break
""",
        language="python",
    )


section = st.sidebar.radio(
    "Раздел",
    [
        "Код решателя",
        "Верификация",
        "Вихревая зона при разных циркуляциях",
        "Вихревая зона при разных диаметрах цилиндра",
    ],
)

if section == "Верификация":
    render_verification()

elif section == "Вихревая зона при разных циркуляциях":
    render_gamma_results()

elif section == "Вихревая зона при разных диаметрах цилиндра":
    render_diameter_results()

else:
    render_solver_code()
