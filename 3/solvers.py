from pathlib import Path
import csv
import argparse

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from fenics import plot

import solve

RESULTS_DIR = Path("results")


ONE_VORTEX_GRIDS = [
    "20",
    "d_1.5",
    "d_1.0",
    "d_0.5",
    "d_0.2",
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
    plt.savefig(out_dir / "psi.png", dpi=300)
    plt.close("all")

    solve.plot_vorticity(
        result["vorticity"],
        title=f"Завихрённость, Г = {gamma:g}",
    )
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
                    tol=1e-3
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
                    "psi_min": result["psi_min"],
                    "final_residual": result["final_residual"],
                    "circulation": float(result["vorticity_gamma"]),
                }

                write_one_row_csv(out_dir / "summary.csv", summary)
                write_csv(out_dir / "history.csv", result["history"])

def run_one_vortex_refinement():
    gamma = -1
    for grid_name in ONE_VORTEX_REFINEMENT_GRIDS:
        # for gamma in ONE_VORTEX_GAMMAS[]:
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
                    tol=1e-3
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
                    "psi_min": result["psi_min"],
                    "final_residual": result["final_residual"],
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

if __name__ == "__main__":
    main()
