#!/bin/bash
set -e

grids=(5 10 20)

for g in "${grids[@]}"; do
	gmsh grid_${g}.geo -2 grid_${g}.msh
done
