from __future__ import annotations

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
    parameters: dict[str, float]
    vertex_count: int
    cell_count: int


def _parse_float(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text)
    if not match:
        return None
    return float(match.group(1))


def parse_geo_parameters(geo_path: Path) -> dict[str, float]:
    text = geo_path.read_text(encoding="utf-8")
    parameters = {}
    for key in ("L", "H", "r1", "l1", "h1", "r2", "l2", "h2", "N"):
        value = _parse_float(rf"{key}\s*=\s*([0-9.]+)", text)
        if value is not None:
            parameters[key] = value
    return parameters


def load_mesh(xml_path: Path) -> tuple[np.ndarray, np.ndarray]:
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


def _classify_case(name: str) -> tuple[str, str]:
    if name.isdigit():
        return "base", f"N = {name}"
    if name.startswith("grid_l_"):
        value = name.replace("grid_l_", "")
        return "distance", f"l2 = {value}"
    if name.startswith("grid_h_"):
        value = name.replace("grid_h_", "")
        return "height", f"h2 = {value}"
    return "other", name


def discover_mesh_cases(mesh_root: Path) -> list[MeshCase]:
    cases: list[MeshCase] = []
    for directory in sorted(path for path in mesh_root.iterdir() if path.is_dir()):
        name = directory.name
        if name.isdigit():
            prefix = f"grid_{name}"
        else:
            prefix = name
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

    def family_value(case: MeshCase):
        if case.family == "base":
            return case.parameters.get("N", 0.0)
        if case.family == "distance":
            return case.parameters.get("l2", 0.0)
        if case.family == "height":
            return case.parameters.get("h2", 0.0)
        return case.label

    return sorted(cases, key=lambda case: (family_order.get(case.family, 9), family_value(case)))


def family_title(family: str) -> str:
    return {
        "base": "Базовая последовательность сеток",
        "distance": "Изменение расстояния между цилиндрами",
        "height": "Изменение вертикальной координаты второго цилиндра",
    }.get(family, family)


def group_cases(cases: list[MeshCase]) -> dict[str, list[MeshCase]]:
    grouped: dict[str, list[MeshCase]] = {"base": [], "distance": [], "height": [], "other": []}
    for case in cases:
        grouped.setdefault(case.family, []).append(case)
    return grouped


def format_parameters(parameters: dict[str, float]) -> list[tuple[str, str]]:
    labels = {
        "L": "Длина канала L",
        "H": "Высота канала H",
        "r1": "Радиус первого цилиндра r1",
        "l1": "Координата l1",
        "h1": "Координата h1",
        "r2": "Радиус второго цилиндра r2",
        "l2": "Координата l2",
        "h2": "Координата h2",
        "N": "Параметр дискретизации N",
    }
    ordered_keys = ["L", "H", "r1", "l1", "h1", "r2", "l2", "h2", "N"]
    result = []
    for key in ordered_keys:
        if key in parameters:
            result.append((labels[key], f"{parameters[key]:.4g}"))
    return result


def build_mesh_figure(case: MeshCase, show_nodes: bool = False, highlight_geometry: bool = True):
    vertices, triangles = load_mesh(case.xml_path)
    triangulation = Triangulation(vertices[:, 0], vertices[:, 1], triangles)

    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.triplot(triangulation, color="#36506c", linewidth=0.35)
    if show_nodes:
        ax.scatter(vertices[:, 0], vertices[:, 1], s=4, color="#b22222", alpha=0.55)

    if highlight_geometry:
        p = case.parameters
        ax.add_patch(Rectangle((0, 0), p.get("L", 2.0), p.get("H", 1.0), fill=False, linewidth=1.2, edgecolor="#111111"))
        ax.add_patch(Circle((p.get("l1", 0.5), p.get("h1", 0.5)), p.get("r1", 0.1875), fill=False, linewidth=1.1, edgecolor="#9a3412"))
        ax.add_patch(Circle((p.get("l2", 1.25), p.get("h2", 0.5)), p.get("r2", 0.1875), fill=False, linewidth=1.1, edgecolor="#9a3412"))

    ax.set_aspect("equal")
    ax.set_xlim(vertices[:, 0].min() - 0.05, vertices[:, 0].max() + 0.05)
    ax.set_ylim(vertices[:, 1].min() - 0.05, vertices[:, 1].max() + 0.05)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"Сетка: {case.label}")
    ax.grid(False)
    return fig


def build_geometry_figure(case: MeshCase):
    p = case.parameters
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.add_patch(Rectangle((0, 0), p.get("L", 2.0), p.get("H", 1.0), fill=False, linewidth=1.5, edgecolor="#111111"))
    ax.add_patch(Circle((p.get("l1", 0.5), p.get("h1", 0.5)), p.get("r1", 0.1875), fill=False, linewidth=1.5, edgecolor="#0f766e"))
    ax.add_patch(Circle((p.get("l2", 1.25), p.get("h2", 0.5)), p.get("r2", 0.1875), fill=False, linewidth=1.5, edgecolor="#0f766e"))

    ax.text(-0.03, 0.5 * p.get("H", 1.0), r"$\Gamma_3$", ha="right", va="center")
    ax.text(p.get("L", 2.0) + 0.03, 0.5 * p.get("H", 1.0), r"$\Gamma_4$", ha="left", va="center")
    ax.text(0.5 * p.get("L", 2.0), -0.05, r"$\Gamma_1$", ha="center", va="top")
    ax.text(0.5 * p.get("L", 2.0), p.get("H", 1.0) + 0.05, r"$\Gamma_2$", ha="center", va="bottom")
    ax.text(p.get("l1", 0.5), p.get("h1", 0.5), r"$D_1$", ha="center", va="center")
    ax.text(p.get("l2", 1.25), p.get("h2", 0.5), r"$D_2$", ha="center", va="center")

    ax.set_aspect("equal")
    ax.set_xlim(-0.1, p.get("L", 2.0) + 0.1)
    ax.set_ylim(-0.1, p.get("H", 1.0) + 0.1)
    ax.set_axis_off()
    ax.set_title("Схема расчётной области")
    return fig


def mesh_summary_table(cases: list[MeshCase]) -> list[dict[str, str]]:
    def fmt(value: float | None) -> str:
        if value is None:
            return "—"
        return f"{value:.4g}"

    rows = []
    for case in cases:
        rows.append(
            {
                "Набор": family_title(case.family),
                "Сценарий": case.label,
                "Вершины": f"{case.vertex_count}",
                "Треугольники": f"{case.cell_count}",
                "l2": fmt(case.parameters.get("l2")),
                "h2": fmt(case.parameters.get("h2")),
                "N": fmt(case.parameters.get("N")),
            }
        )
    return rows


def extract_code_excerpt(path: Path, start_marker: str, end_marker: str | None = None) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.find(start_marker)
    if start == -1:
        return text
    if end_marker is None:
        return text[start:]
    end = text.find(end_marker, start)
    if end == -1:
        return text[start:]
    return text[start:end]


def try_compute_solution(case: MeshCase):
    try:
        from fenics import Constant, DirichletBC, Expression, FacetNormal, Function, FunctionSpace, Measure, Mesh, MeshFunction, TestFunction, TrialFunction, assemble, dot, dx, grad, solve
    except Exception as exc:  # pragma: no cover
        return None, None, f"FEniCS недоступен: {exc}"

    try:
        mesh = Mesh(str(case.xml_path))
        boundaries = MeshFunction("size_t", mesh, str(case.facet_path))
        ds = Measure("ds", domain=mesh, subdomain_data=boundaries)

        space = FunctionSpace(mesh, "CG", 2)
        inlet = Expression("x[1]", degree=2)
        boundary_conditions = [
            DirichletBC(space, Constant(0.0), boundaries, 1),
            DirichletBC(space, Constant(1.0), boundaries, 2),
            DirichletBC(space, Constant(0.5), boundaries, 5),
            DirichletBC(space, Constant(0.5), boundaries, 6),
            DirichletBC(space, inlet, boundaries, 3),
        ]

        u = TrialFunction(space)
        v = TestFunction(space)
        a = dot(grad(u), grad(v)) * dx
        l_form = Constant(0.0) * v * dx

        solution = Function(space)
        solve(a == l_form, solution, boundary_conditions)

        n = FacetNormal(mesh)
        flux = dot(grad(solution), n)
        gamma_1 = assemble(flux * ds(5))
        gamma_2 = assemble(flux * ds(6))

        vertices, triangles = load_mesh(case.xml_path)
        values = solution.compute_vertex_values(mesh)
        triangulation = Triangulation(vertices[:, 0], vertices[:, 1], triangles)

        fig, ax = plt.subplots(figsize=(8, 3.8))
        contour = ax.tricontourf(triangulation, values, levels=20, cmap="viridis")
        ax.triplot(triangulation, linewidth=0.15, color="white", alpha=0.35)
        ax.set_aspect("equal")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Поле функции тока, построенное по текущему solver")
        plt.colorbar(contour, ax=ax)
        return fig, {"Gamma1": float(gamma_1), "Gamma2": float(gamma_2)}, None
    except Exception as exc:  # pragma: no cover
        return None, None, f"Не удалось выполнить расчёт: {exc}"
