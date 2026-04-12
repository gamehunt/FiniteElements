from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.tri import Triangulation


@dataclass(frozen=True)
class MeshCase:
    name: str
    family: str
    label: str
    geo_path: Path
    xml_path: Path
    facet_path: Path
    msh_path: Path
    parameters: dict
    vertex_count: int
    cell_count: int


def _parse_float(pattern, text):
    match = re.search(pattern, text)
    if not match:
        return None
    return float(match.group(1))


def parse_geo_parameters(geo_path):
    text = geo_path.read_text(encoding="utf-8")
    parameters = {}
    for key in ("L", "H", "r1", "l1", "h1", "r2", "l2", "h2", "N"):
        value = _parse_float(rf"{key}\s*=\s*([0-9.]+)", text)
        if value is not None:
            parameters[key] = value
    return parameters


def load_mesh(xml_path):
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


def _classify_case(name):
    if name.isdigit():
        return "base", f"N = {name}"
    if name.startswith("grid_l_"):
        return "distance", f"l_2 = {name.replace('grid_l_', '')}"
    if name.startswith("grid_h_"):
        return "height", f"h_2 = {name.replace('grid_h_', '')}"
    return "other", name


def discover_mesh_cases(mesh_root):
    cases = []
    for directory in sorted(path for path in mesh_root.iterdir() if path.is_dir()):
        name = directory.name
        prefix = f"grid_{name}" if name.isdigit() else name
        xml_path = directory / f"{prefix}.xml"
        geo_path = directory / f"{prefix}.geo"
        facet_path = directory / f"{prefix}_facet_region.xml"
        msh_path = directory / f"{prefix}.msh"
        if not (xml_path.exists() and geo_path.exists() and facet_path.exists() and msh_path.exists()):
            continue

        parameters = parse_geo_parameters(geo_path)
        vertices, triangles = load_mesh(xml_path)
        family, label = _classify_case(name)
        cases.append(
            MeshCase(
                name=name,
                family=family,
                label=label,
                geo_path=geo_path,
                xml_path=xml_path,
                facet_path=facet_path,
                msh_path=msh_path,
                parameters=parameters,
                vertex_count=len(vertices),
                cell_count=len(triangles),
            )
        )

    family_order = {"base": 0, "distance": 1, "height": 2, "other": 3}

    def sort_value(case):
        if case.family == "base":
            return case.parameters.get("N", 0.0)
        if case.family == "distance":
            return case.parameters.get("l2", 0.0)
        if case.family == "height":
            return case.parameters.get("h2", 0.0)
        return case.label

    return sorted(cases, key=lambda case: (family_order.get(case.family, 9), sort_value(case)))


def group_cases(cases):
    grouped = {"base": [], "distance": [], "height": [], "other": []}
    for case in cases:
        grouped.setdefault(case.family, []).append(case)
    return grouped


def safe_first(cases):
    return cases[0] if cases else None


def family_title(family):
    return {
        "base": "Последовательность сеточного сгущения",
        "distance": "Симметричные сценарии",
        "height": "Несимметричные сценарии",
    }.get(family, family)


def format_geometry_parameters(parameters):
    labels = {
        "L": "L",
        "H": "H",
        "r1": "r_1",
        "r2": "r_2",
        "l1": "l_1",
        "l2": "l_2",
        "h1": "h_1",
        "h2": "h_2",
    }
    ordered = ["L", "H", "r1", "r2", "l1", "l2", "h1", "h2"]
    return [(labels[key], f"{parameters[key]:.4g}") for key in ordered if key in parameters]


def build_geometry_figure(case):
    p = case.parameters
    fig, ax = plt.subplots(figsize=(8.0, 3.0))
    ax.add_patch(Rectangle((0, 0), p.get("L", 2.0), p.get("H", 1.0), fill=False, linewidth=1.5, edgecolor="#111111"))
    ax.add_patch(Circle((p.get("l1", 0.5), p.get("h1", 0.5)), p.get("r1", 0.1875), fill=False, linewidth=1.4, edgecolor="#14532d"))
    ax.add_patch(Circle((p.get("l2", 1.25), p.get("h2", 0.5)), p.get("r2", 0.1875), fill=False, linewidth=1.4, edgecolor="#14532d"))
    ax.text(-0.04, 0.5 * p.get("H", 1.0), r"$\Gamma_3$", ha="right", va="center")
    ax.text(p.get("L", 2.0) + 0.04, 0.5 * p.get("H", 1.0), r"$\Gamma_4$", ha="left", va="center")
    ax.text(0.5 * p.get("L", 2.0), -0.05, r"$\Gamma_1$", ha="center", va="top")
    ax.text(0.5 * p.get("L", 2.0), p.get("H", 1.0) + 0.05, r"$\Gamma_2$", ha="center", va="bottom")
    ax.text(p.get("l1", 0.5), p.get("h1", 0.5), r"$D_1$", ha="center", va="center")
    ax.text(p.get("l2", 1.25), p.get("h2", 0.5), r"$D_2$", ha="center", va="center")
    ax.set_aspect("equal")
    ax.set_xlim(-0.1, p.get("L", 2.0) + 0.1)
    ax.set_ylim(-0.1, p.get("H", 1.0) + 0.1)
    ax.set_axis_off()
    return fig


def build_mesh_figure(case, show_nodes=False):
    vertices, triangles = load_mesh(case.xml_path)
    triangulation = Triangulation(vertices[:, 0], vertices[:, 1], triangles)
    fig, ax = plt.subplots(figsize=(10.0, 4.2))
    ax.triplot(triangulation, color="#334155", linewidth=0.35)
    if show_nodes:
        ax.scatter(vertices[:, 0], vertices[:, 1], s=3, color="#991b1b", alpha=0.45)
    ax.set_aspect("equal")
    ax.set_xlim(vertices[:, 0].min() - 0.05, vertices[:, 0].max() + 0.05)
    ax.set_ylim(vertices[:, 1].min() - 0.05, vertices[:, 1].max() + 0.05)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(case.label)
    return fig


def build_solution_figure(solution, degree):
    import matplotlib.pyplot as plt
    from fenics import plot

    fig, ax = plt.subplots(figsize=(10.0, 4.2))
    plt.sca(ax)
    contour = plot(solution, title=f"Поле функции тока, p = {degree}")
    plt.colorbar(contour, ax=ax)
    ax.set_aspect("equal")
    return fig


def build_circulation_chart(rows, x_labels, title):
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    x = np.arange(len(rows))
    gamma_1 = [row["gamma_1"] for row in rows]
    gamma_2 = [row["gamma_2"] for row in rows]
    ax.plot(x, gamma_1, marker="o", linewidth=1.6, label=r"$\Gamma_1$")
    ax.plot(x, gamma_2, marker="s", linewidth=1.6, label=r"$\Gamma_2$")
    ax.set_xticks(x, x_labels)
    ax.set_title(title)
    ax.set_ylabel("Циркуляция")
    ax.grid(True, axis="y", linewidth=0.3, alpha=0.5)
    ax.legend()
    return fig
