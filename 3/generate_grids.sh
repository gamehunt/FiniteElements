#!/bin/bash
set -e

l1_base=1
l2_base=2
grids=(5 10 20)

rm -rf grids/*

for g in "${grids[@]}"; do
    name=grid_${g}
    par=grids/$g
    mkdir -p $par
    sed -e "s/%SIZE%/${g}/g" -e "s/%L1%/${l1_base}/g" -e "s/%L2%/${l2_base}/g" grid_template.geo >$par/$name.geo
    gmsh $par/${name}.geo -2 -format msh2 $par/${name}.msh
    dolfin-convert $par/${name}.msh $par/${name}.xml
done

# r = 0.75 0.25 0.1
d_values=(1.5 0.5 0.2)
l1_values=(0.75 1.25 1.4) 
l2_values=(2.25 1.75 1.6)

for i in "${!l1_values[@]}"; do
    l1=${l1_values[$i]}
    l2=${l2_values[$i]}
	d=${d_values[$i]}
	name=grid_d_${d}
    par=grids/d_${d}
    mkdir -p $par
    sed -e "s/%SIZE%/20/g" -e "s/%L1%/${l1}/g" -e "s/%L2%/${l2}/g" grid_template.geo >$par/$name.geo
    gmsh $par/${name}.geo -2 -format msh2 $par/${name}.msh
    dolfin-convert $par/${name}.msh $par/${name}.xml
done
