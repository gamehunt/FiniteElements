#!/bin/bash
set -e

l1_base=1
l2_base=2
grids=(5 10 20)

rm -rf grids/*

generate_grid() { # density template l1 l2 custom_name
    local density=$1
    local template=$2
    local l1=$3
    local l2=$4
    local custom_name=$5

    local par=grids/${density}
    local name=grid_${density}

    if [ ! -z "$custom_name" ]; then
        par=grids/${custom_name}
        name=grid_${custom_name}
    fi

    mkdir -p $par

    sed \
        -e "s/%SIZE%/${density}/g" \
        -e "s/%L1%/${l1}/g" \
        -e "s/%L2%/${l2}/g" \
        ${template}.geo >$par/${name}.geo

    gmsh $par/${name}.geo -2 -format msh2 $par/${name}.msh
    dolfin-convert $par/${name}.msh $par/${name}.xml
}

# Полуцилиндр по плотности
for g in "${grids[@]}"; do
    generate_grid $g "grid_template" ${l1_base} ${l2_base}
done

# Размеры препятствия
d_values=(1.5 0.5 0.2)
l1_values=(0.75 1.25 1.4)
l2_values=(2.25 1.75 1.6)

# Полуцилиндр разных размеров
for i in "${!l1_values[@]}"; do
    generate_grid 20 "grid_template" ${l1_values[$i]} ${l2_values[$i]} "d_${d_values[$i]}"
done

# Цилиндр базовый
generate_grid 20 "grid_template_full" ${l1_base} ${l2_base} "cyl_d_1.0"

# Цилиндр разных размеров
for i in "${!l1_values[@]}"; do
    generate_grid 20 "grid_template_full" ${l1_values[$i]} ${l2_values[$i]} "cyl_d_${d_values[$i]}"
done
