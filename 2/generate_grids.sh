#!/bin/bash
set -e

grids=(5 10 20)

for g in "${grids[@]}"; do
	name=grid_${g}
	par=mesh/$g
	mkdir -p $par
	sed "s/%SIZE%/${g}/g" grid_template.geo > $par/$name.geo
	gmsh $par/${name}.geo -2 -format msh2 $par/${name}.msh
	dolfin-convert $par/${name}.msh $par/${name}.xml
done
