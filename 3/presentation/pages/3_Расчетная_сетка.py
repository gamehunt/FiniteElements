from pathlib import Path
import re
import xml.etree.ElementTree as ET

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.tri import Triangulation


# ------------------------------------------------------------
# Поиск корня проекта
# ------------------------------------------------------------


def find_project_root():
    current = Path(__file__).resolve()

    for parent in [current.parent, *current.parents]:
        if (parent / "grids").exists():
            return parent

    raise RuntimeError("Не удалось найти корень проекта: папка grids/ не найдена.")


PROJECT_ROOT = find_project_root()
GRIDS_ROOT = PROJECT_ROOT / "grids"


# ------------------------------------------------------------
# Загрузка сетки
# ------------------------------------------------------------


def load_mesh_xml(xml_path: Path):
    root = ET.parse(xml_path).getroot()

    vertices_parent = root.find(".//vertices")
    cells_parent = root.find(".//cells")

    if vertices_parent is None or cells_parent is None:
        raise ValueError(f"Некорректный mesh XML: {xml_path}")

    vertices = np.zeros((int(vertices_parent.attrib["size"]), 2), dtype=float)

    for vertex in vertices_parent:
        idx = int(vertex.attrib["index"])
        vertices[idx, 0] = float(vertex.attrib["x"])
        vertices[idx, 1] = float(vertex.attrib["y"])

    triangles = np.zeros((int(cells_parent.attrib["size"]), 3), dtype=int)

    for cell in cells_parent:
        idx = int(cell.attrib["index"])
        triangles[idx, 0] = int(cell.attrib["v0"])
        triangles[idx, 1] = int(cell.attrib["v1"])
        triangles[idx, 2] = int(cell.attrib["v2"])

    return vertices, triangles


def parse_geo_parameters(geo_path: Path):
    params = {}

    if not geo_path.exists():
        return params

    text = geo_path.read_text(encoding="utf-8", errors="ignore")

    for key in ("L", "H", "l1", "l2", "N"):
        match = re.search(rf"{key}\s*=\s*([0-9.]+)", text)
        if match:
            params[key] = float(match.group(1))

    if "l1" in params and "l2" in params:
        params["D"] = params["l2"] - params["l1"]
        params["r_c"] = 0.5 * params["D"]

    return params


def discover_grids():
    cases = []

    for directory in sorted(p for p in GRIDS_ROOT.iterdir() if p.is_dir()):
        name = directory.name
        prefix = f"grid_{name}"

        xml_path = directory / f"{prefix}.xml"
        geo_path = directory / f"{prefix}.geo"

        if not xml_path.exists():
            continue

        vertices, triangles = load_mesh_xml(xml_path)
        params = parse_geo_parameters(geo_path)

        y_min = float(vertices[:, 1].min())
        y_max = float(vertices[:, 1].max())
        height = y_max - y_min

        is_full = name == "full" or height > 1.5

        if name.startswith("cyl_d_"):
            label = f"Цилиндр D = {name.replace('cyl_d_', '')}"
            family = "cylinder"
        elif name.isdigit():
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
                "is_full": is_full,
                "xml_path": xml_path,
                "geo_path": geo_path,
                "vertices": vertices,
                "triangles": triangles,
                "params": params,
                "vertex_count": len(vertices),
                "cell_count": len(triangles),
                "x_min": float(vertices[:, 0].min()),
                "x_max": float(vertices[:, 0].max()),
                "y_min": y_min,
                "y_max": y_max,
                "height": height,
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


# ------------------------------------------------------------
# Параметры начальной зоны
# ------------------------------------------------------------


def estimate_l2(case):
    params = case["params"]

    if "l2" in params:
        return float(params["l2"])

    if case["name"].startswith("d_"):
        try:
            d = float(case["name"].replace("d_", ""))
            xc = 1.5
            return xc + 0.5 * d
        except ValueError:
            pass

    return 2.0


def estimate_rc(case):
    params = case["params"]

    if "r_c" in params:
        return float(params["r_c"])

    if case["name"].startswith("d_"):
        try:
            return 0.5 * float(case["name"].replace("d_", ""))
        except ValueError:
            pass

    return 0.5


# ------------------------------------------------------------
# Отрисовка сетки и начальной области
# ------------------------------------------------------------


def draw_vortex_seed(ax, case, l2, rc):
    y_min = case["y_min"]
    y_max = case["y_max"]
    yc = 0.5 * (y_min + y_max)

    if case["is_full"]:
        bottom_zone = patches.Rectangle(
            (l2, yc - rc),
            rc,
            rc,
            linewidth=1.8,
            edgecolor="tab:blue",
            facecolor="none",
            hatch="///",
            label=r"$D_-^0$",
        )

        top_zone = patches.Rectangle(
            (l2, yc),
            rc,
            rc,
            linewidth=1.8,
            edgecolor="tab:red",
            facecolor="none",
            hatch="\\\\",
            label=r"$D_+^0$",
        )

        ax.add_patch(bottom_zone)
        ax.add_patch(top_zone)

    else:
        wake_zone = patches.Rectangle(
            (l2, y_min),
            rc,
            rc,
            linewidth=1.8,
            edgecolor="tab:red",
            facecolor="none",
            hatch="///",
            label=r"$D^0$",
        )

        ax.add_patch(wake_zone)


def draw_mesh(case):
    vertices = case["vertices"]
    triangles = case["triangles"]

    triangulation = Triangulation(vertices[:, 0], vertices[:, 1], triangles)

    l2 = estimate_l2(case)
    rc = estimate_rc(case)

    fig, ax = plt.subplots(figsize=(10.5, 4.3))

    ax.triplot(triangulation, color="#334155", linewidth=0.35)

    draw_vortex_seed(ax, case, l2, rc)

    dx = case["x_max"] - case["x_min"]
    dy = case["y_max"] - case["y_min"]

    ax.set_xlim(case["x_min"] - 0.03 * dx, case["x_max"] + 0.03 * dx)
    ax.set_ylim(case["y_min"] - 0.05 * dy, case["y_max"] + 0.05 * dy)

    ax.set_aspect("equal")
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    ax.set_title(case["label"])
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()

    return fig, l2, rc


# ------------------------------------------------------------
# Streamlit
# ------------------------------------------------------------

st.title("Расчётная сетка")

cases = discover_grids()

if not cases:
    st.warning(f"Сетки не найдены в папке `{GRIDS_ROOT}`.")
    st.stop()

case = st.selectbox(
    "Выбор расчетной сетки",
    cases,
    format_func=lambda c: c["label"],
)

fig, l2, rc = draw_mesh(case)
st.pyplot(fig, use_container_width=True)

# ------------------------------------------------------------
# Параметры сетки через колонки
# ------------------------------------------------------------


col1, col2 = st.columns(2)

with col1:
    st.metric("Вершины", case["vertex_count"])

with col2:
    st.metric("Треугольники", case["cell_count"])


# ------------------------------------------------------------
# Правило начальной вихревой области
# ------------------------------------------------------------

if case["is_full"]:
    st.subheader("Правило задания начальных вихревых областей")

    r"""
    Для полной сетки задаются две начальные вихревые области:
    нижняя область $D_-^0$ и верхняя область $D_+^0$.

    Сначала определяется линия симметрии канала:

    $$
    y_c=\frac{y_{\min}+y_{\max}}{2}.
    $$
    """

    st.code(
        """
y_min = mesh.coordinates()[:, 1].min()
y_max = mesh.coordinates()[:, 1].max()

yc = 0.5 * (y_min + y_max)
""",
        language="python",
    )

    r"""
    Нижняя начальная область располагается за цилиндром и ниже линии симметрии:

    $$
    D_-^0=
    \left\{
    (x_1,x_2):
    l_2<x_1<l_2+r_c,\quad
    y_c-r_c<x_2<y_c
    \right\}.
    $$
    """

    st.code(
        """
wake_bottom = WakeZone(
    l2=l2,
    y0=yc - rc,
    rc=rc,
    psi_value=-2.0,
    degree=degree,
)
""",
        language="python",
    )

    r"""
    Верхняя начальная область располагается за цилиндром и выше линии симметрии:

    $$
    D_+^0=
    \left\{
    (x_1,x_2):
    l_2<x_1<l_2+r_c,\quad
    y_c<x_2<y_c+r_c
    \right\}.
    $$
    """

    st.code(
        """
wake_top = WakeZone(
    l2=l2,
    y0=yc,
    rc=rc,
    psi_value=-2.0,
    degree=degree,
)
""",
        language="python",
    )

    r"""
    Эти прямоугольники используются только как начальное приближение.
    После начала итерационного процесса вихревая область определяется уже
    по знаку функции тока:

    $$
    D_+^k=
    \left\{
    x:\psi^k(x)<0,\quad x_2>y_c
    \right\},
    $$

    $$
    D_-^k=
    \left\{
    x:\psi^k(x)<0,\quad x_2<y_c
    \right\}.
    $$
    """

    st.code(
        """
top_mask = (psi_values < 0.0) & (coords[:, 1] > yc)
bottom_mask = (psi_values < 0.0) & (coords[:, 1] < yc)
""",
        language="python",
    )

else:
    st.subheader("Правило задания начальной вихревой области")

    r"""
    Для выбранной сетки задаётся одна начальная вихревая область.
    Она располагается за цилиндром.

    Сначала определяется правая граница цилиндра $l_2$, размер начальной
    области $r_c$, а также нижняя граница расчётной области $y_{\min}$.
    """

    st.code(
        """
l2 = get_l2_from_mesh(mesh, boundaries)
rc = 0.5
y_min = mesh.coordinates()[:, 1].min()
""",
        language="python",
    )

    r"""
    Начальная область задаётся прямоугольником:

    $$
    D^0=
    \left\{
    (x_1,x_2):
    l_2<x_1<l_2+r_c,\quad
    y_{\min}<x_2<y_{\min}+r_c
    \right\}.
    $$
    """

    st.code(
        """
wake_zone = WakeZone(
    l2=l2,
    r_cyl=rc,
    psi_value=-0.05,
    degree=degree,
)
""",
        language="python",
    )

    r"""
    После итераций финальная вихревая область уже не обязана совпадать
    с этим прямоугольником. Она определяется по условию:

    $$
    D^k=
    \left\{
    x:\psi^k(x)<0
    \right\}.
    $$
    """

    st.code(
        """
vortex_mask = psi_values < 0.0
""",
        language="python",
    )
