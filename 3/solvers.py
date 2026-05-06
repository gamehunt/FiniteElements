from pathlib import Path
import csv
import argparse

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from fenics import plot

import solve
import solve_non_symmetrical


RESULTS_DIR = Path("results")


ONE_VORTEX_GRIDS = [
    "d_1.5",
    "d_1.0",
    "d_0.5",
    "d_0.2",
]

TWO_VORTEX_GRIDS = [
    # "cyl_d_1.5",
    "cyl_d_1.0",
    # "cyl_d_0.5",
    # "cyl_d_0.2",
]

ONE_VORTEX_REFINEMENT_GRIDS = [
    "5",
    "10",
    "20",
]

DEGREES = [1, 2, 3]

ONE_VORTEX_GAMMAS = [
    -1.0,
    -2.5,
    -5.0,
]

TWO_VORTEX_GAMMAS = [
    (-1.0, 1.0),
    (-2.5, 2.5),
    (-5.0, 5.0),
    # Несимметричный случай
    (-1.5, -0.7),
]


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        return

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_one_row_csv(path, row):
    write_csv(path, [row])


def save_one_vortex_images(result: dict, out_dir: Path, gamma: float):
    out_dir.mkdir(parents=True, exist_ok=True)

    solve.plot_solution(
        result["solution"],
        title=f"Функция тока, Г = {gamma:g}",
    )
    plt.tight_layout()
    plt.savefig(out_dir / "psi.png", dpi=200)
    plt.close("all")

    solve.plot_vorticity(
        result["vorticity"],
        title=f"Завихрённость, Г = {gamma:g}",
    )
    plt.tight_layout()
    plt.savefig(out_dir / "omega.png", dpi=200)
    plt.close("all")


def save_two_vortex_images(
    result: dict, out_dir: Path, gamma_top: float, gamma_bot: float
):
    out_dir.mkdir(parents=True, exist_ok=True)

    solve_non_symmetrical.plot_solution(
        result["solution"],
        title=f"Функция тока, Г₊ = {gamma_top:g}, Г₋ = {gamma_bot:g}",
    )
    plt.tight_layout()
    plt.savefig(out_dir / "psi.png", dpi=200)
    plt.close("all")

    plt.figure()
    c = plot(
        result["vorticity"],
        title=f"Завихрённость, Г₊ = {gamma_top:g}, Г₋ = {gamma_bot:g}",
    )
    plt.colorbar(c)
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.tight_layout()
    plt.savefig(out_dir / "omega.png", dpi=200)
    plt.close("all")


def run_one_vortex():
    for grid_name in ONE_VORTEX_GRIDS:
        for gamma in ONE_VORTEX_GAMMAS:
            for degree in DEGREES:
                print()
                print("=" * 80)
                print(
                    f"Одиночный вихрь: grid={grid_name}, gamma={gamma:g}, degree={degree}"
                )
                print("=" * 80)

                result = solve.solve_problem(
                    grid_name=grid_name,
                    degree=degree,
                    gamma=gamma,
                )

                out_dir = (
                    RESULTS_DIR
                    / "one_vortex"
                    / grid_name
                    / f"gamma_{gamma:g}"
                    / f"degree_{degree}"
                )

                save_one_vortex_images(result, out_dir, gamma)

                summary = {
                    "solver": "solve.py",
                    "case": "one_vortex",
                    "grid": grid_name,
                    "gamma": gamma,
                    "degree": degree,
                    "vertices": result["mesh"].num_vertices(),
                    "cells": result["mesh"].num_cells(),
                    "dofs": result["dofs"],
                    "iterations": result["iterations"],
                    "error_final": result["error_final"],
                    "vortex_area": result["vortex_area"],
                    "omega_value": result["omega_value"],
                    "circulation": float(result["vorticity_gamma"]),
                }

                write_one_row_csv(out_dir / "summary.csv", summary)
                write_csv(out_dir / "history.csv", result["history"])


def run_two_vortex():
    for grid_name in TWO_VORTEX_GRIDS:
        for gamma_top, gamma_bot in TWO_VORTEX_GAMMAS:
            for degree in DEGREES:
                print()
                print("=" * 80)
                print(
                    f"Два вихря: grid={grid_name}, "
                    f"gamma_top={gamma_top:g}, gamma_bot={gamma_bot:g}, degree={degree}"
                )
                print("=" * 80)

                result = solve_non_symmetrical.solve_problem(
                    grid_name=grid_name,
                    degree=degree,
                    gamma_top=gamma_top,
                    gamma_bot=gamma_bot,
                )

                out_dir = (
                    RESULTS_DIR
                    / "two_vortex"
                    / grid_name
                    / f"gamma_top_{gamma_top:g}_gamma_bot_{gamma_bot:g}"
                    / f"degree_{degree}"
                )

                save_two_vortex_images(result, out_dir, gamma_top, gamma_bot)

                summary = {
                    "solver": "solve_non_symmetrical.py",
                    "case": "two_vortex",
                    "grid": grid_name,
                    "gamma_top": gamma_top,
                    "gamma_bot": gamma_bot,
                    "degree": degree,
                    "vertices": result["mesh"].num_vertices(),
                    "cells": result["mesh"].num_cells(),
                    "dofs": result["dofs"],
                    "iterations": result["iterations"],
                    "error_final": result["error_final"],
                    "A_top": result["A_top"],
                    "A_bot": result["A_bot"],
                    "omega_top": result["omega_top"],
                    "omega_bot": result["omega_bot"],
                    "yc": result["yc"],
                    "rc": result["rc"],
                }

                write_one_row_csv(out_dir / "summary.csv", summary)
                write_csv(out_dir / "history.csv", result["history"])


def run_one_vortex_refinement():
    for grid_name in ONE_VORTEX_REFINEMENT_GRIDS:
        for gamma in ONE_VORTEX_GAMMAS:
            for degree in DEGREES:
                print()
                print("=" * 80)
                print(
                    f"Одиночный вихрь, сгущение: grid={grid_name}, gamma={gamma:g}, degree={degree}"
                )
                print("=" * 80)

                result = solve.solve_problem(
                    grid_name=grid_name,
                    degree=degree,
                    gamma=gamma,
                )

                out_dir = (
                    RESULTS_DIR
                    / "one_vortex_refinement"
                    / grid_name
                    / f"gamma_{gamma:g}"
                    / f"degree_{degree}"
                )

                save_one_vortex_images(result, out_dir, gamma)

                summary = {
                    "solver": "solve.py",
                    "case": "one_vortex_refinement",
                    "grid": grid_name,
                    "gamma": gamma,
                    "degree": degree,
                    "vertices": result["mesh"].num_vertices(),
                    "cells": result["mesh"].num_cells(),
                    "dofs": result["dofs"],
                    "iterations": result["iterations"],
                    "error_final": result["error_final"],
                    "vortex_area": result["vortex_area"],
                    "omega_value": result["omega_value"],
                    "circulation": float(result["vorticity_gamma"]),
                }

                write_one_row_csv(out_dir / "summary.csv", summary)
                write_csv(out_dir / "history.csv", result["history"])


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--solver",
        choices=["one", "two", "all"],
        default="all",
    )

    parser.add_argument(
        "--mode",
        choices=["geometry", "refinement", "all"],
        default="all",
    )

    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)

    if args.solver in ("one", "all"):
        if args.mode in ("geometry", "all"):
            run_one_vortex()

        if args.mode in ("refinement", "all"):
            run_one_vortex_refinement()

    if args.solver in ("two", "all"):
        run_two_vortex()


if __name__ == "__main__":
    main()
