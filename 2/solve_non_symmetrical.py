from fenics import *
import matplotlib.pyplot as plt
import sys

pos    = sys.argv[1]
degree = 2

mesh = Mesh(f'mesh/h_{pos}/grid_h_{pos}.xml')
boundaries = MeshFunction("size_t", mesh, f'mesh/h_{pos}/grid_h_{pos}_facet_region.xml')
ds = Measure("ds", subdomain_data=boundaries)

# Нормаль
n = FacetNormal(mesh)

V = FunctionSpace(mesh, "CG", degree)

# Условие на входе в канал
u_1 = Expression("x[1]", degree=degree)

# -------------------------
# 1. ОСНОВНОЕ РЕШЕНИЕ u0
# -------------------------
bcs0 = [
    DirichletBC(V, Constant(0.0), boundaries, 1),  # низ
    DirichletBC(V, Constant(1.0), boundaries, 2),  # верх
    DirichletBC(V, Constant(0.0), boundaries, 5),  # цилиндр 1
    DirichletBC(V, Constant(0.0), boundaries, 6),  # цилиндр 2
    DirichletBC(V, u_1, boundaries, 3)             # вход
]

u = TrialFunction(V)
v = TestFunction(V)
f = Constant(0.0)  
a = dot(grad(u), grad(v)) * dx
L = f * v * dx

u0 = Function(V)
solve(a == L, u0, bcs0)

# -------------------------
# 2. ВСПОМОГАТЕЛЬНАЯ u1
# (возбуждаем цилиндр 1)
# -------------------------
bcs1 = [
    DirichletBC(V, Constant(0.0), boundaries, 1),
    DirichletBC(V, Constant(0.0), boundaries, 2),
    DirichletBC(V, Constant(1.0), boundaries, 5),  # цилиндр 1
    DirichletBC(V, Constant(0.0), boundaries, 6),  # цилиндр 2
    DirichletBC(V, Constant(0.0), boundaries, 3)
]

u1 = Function(V)
solve(a == L, u1, bcs1)

# -------------------------
# 3. ВСПОМОГАТЕЛЬНАЯ u2
# (возбуждаем цилиндр 2)
# -------------------------
bcs2 = [
    DirichletBC(V, Constant(0.0), boundaries, 1),
    DirichletBC(V, Constant(0.0), boundaries, 2),
    DirichletBC(V, Constant(0.0), boundaries, 5),
    DirichletBC(V, Constant(1.0), boundaries, 6),  # цилиндр 2
    DirichletBC(V, Constant(0.0), boundaries, 3)
]

u2 = Function(V)
solve(a == L, u2, bcs2)

# -------------------------
# 4. ЦИРКУЛЯЦИИ
# -------------------------
flux0 = dot(grad(u0), n)
flux1 = dot(grad(u1), n)
flux2 = dot(grad(u2), n)

# для каждого цилиндра
# цилиндр 1 (id=5)
c01 = assemble(flux0 * ds(5))
c11 = assemble(flux1 * ds(5))
c21 = assemble(flux2 * ds(5))

# цилиндр 2 (id=6)
c02 = assemble(flux0 * ds(6))
c12 = assemble(flux1 * ds(6))
c22 = assemble(flux2 * ds(6))

# print("Циркуляции:")
# print("Cylinder 1:", c01, c11, c21)
# print("Cylinder 2:", c02, c12, c22)

# -------------------------
# 5. РЕШАЕМ СИСТЕМУ НА kappa
# -------------------------
import numpy as np

A = np.array([
    [c11, c21],
    [c12, c22]
])

b = -np.array([c01, c02])  # хотим Γ = 0

kappa = np.linalg.solve(A, b)

k1, k2 = kappa
print(f"kappa1 = {k1}, kappa2 = {k2}")

# -------------------------
# 6. ФИНАЛЬНОЕ РЕШЕНИЕ
# -------------------------
u_final = Function(V)
u_final.vector()[:] = (
    u0.vector()
    + k1 * u1.vector()
    + k2 * u2.vector()
)

# левая точка - значение на границе цилиндра
p = Point(1.25 - 0.1875, float(pos))
print('На границе второго цилиндра: psi=', u_final(p))

# -------------------------
# ПРОВЕРКА
# -------------------------
# flux_final = dot(grad(u_final), n)
#
# Gamma1 = assemble(flux_final * ds(5))
# Gamma2 = assemble(flux_final * ds(6))
#
# print("Итоговые циркуляции:")
# print("Gamma1 =", Gamma1)
# print("Gamma2 =", Gamma2)

c = plot(u_final, title="Решение")
plt.colorbar(c)
plt.show()
