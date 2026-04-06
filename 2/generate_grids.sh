#!/bin/bash
set -e

h_base=0.5
l_base=1.25
size_base=20
grids=(5 10 20)

for g in "${grids[@]}"; do
    name=grid_${g}
    par=mesh/$g
    mkdir -p $par
    sed -e "s/%SIZE%/${g}/g" -e "s/%LENGTH%/${l_base}/g" -e "s/%HEIGHT%/${h_base}/g" grid_template.geo >$par/$name.geo
    gmsh $par/${name}.geo -2 -format msh2 $par/${name}.msh
    dolfin-convert $par/${name}.msh $par/${name}.xml
done

lenghts=(1.10 1.25 1.40)

for l in "${lenghts[@]}"; do
    name=grid_l_${l}
    par=mesh/$name
    mkdir -p $par
    sed -e "s/%SIZE%/${size_base}/g" -e "s/%LENGTH%/${l}/g" -e "s/%HEIGHT%/${h_base}/g" grid_template.geo >$par/$name.geo
    gmsh $par/${name}.geo -2 -format msh2 $par/${name}.msh
    dolfin-convert $par/${name}.msh $par/${name}.xml
done

heights=(0.35 0.50 0.65)

for h in "${heights[@]}"; do
    name=grid_h_${h}
    par=mesh/$name
    mkdir -p $par
    sed -e "s/%SIZE%/${size_base}/g" -e "s/%LENGTH%/${l_base}/g" -e "s/%HEIGHT%/${h}/g" grid_template.geo >$par/$name.geo
    gmsh $par/${name}.geo -2 -format msh2 $par/${name}.msh
    dolfin-convert $par/${name}.msh $par/${name}.xml
done
