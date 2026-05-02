#!/bin/bash
set -e

l1_base=1
l2_base=2
grids=(5 10 20)

for g in "${grids[@]}"; do
    name=grid_${g}
    par=grids/$g
    mkdir -p $par
    sed -e "s/%SIZE%/${g}/g" -e "s/%L1%/${l1_base}/g" -e "s/%L2%/${l2_base}/g" grid_template.geo >$par/$name.geo
    gmsh $par/${name}.geo -2 -format msh2 $par/${name}.msh
    dolfin-convert $par/${name}.msh $par/${name}.xml
done
