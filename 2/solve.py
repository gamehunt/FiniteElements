from fenics import *
import matplotlib.pyplot as plt
import sys

size   = sys.argv[1]
degree = int(sys.argv[2])

mesh = Mesh(f'mesh/{size}/grid_{size}.xml')
boundaries = MeshFunction("size_t", mesh, f'mesh/{size}/grid_{size}_facet_region.xml')

ds = Measure("ds", subdomain_data=boundaries)

  
V = FunctionSpace(mesh, "CG", degree)

# Условие на входе в канал
u_1 = Expression("x[1]", degree=degree)

# Граничные условия
bcs = [DirichletBC(V, Constant(0.0), boundaries, 1), # Низ
       DirichletBC(V, Constant(1.0), boundaries, 2), # Верх
       DirichletBC(V, Constant(0.5), boundaries, 5), # Цилиндр 1
       DirichletBC(V, Constant(0.5), boundaries, 6), # Цилиндр 2
       DirichletBC(V, u_1, boundaries, 3)] # Лево (вход)
# На выходе естественные граничные условия (вроде)

# Вариационная задача
u = TrialFunction(V)
v = TestFunction(V)
f = Constant(0.0)  
a = dot(grad(u), grad(v)) * dx
L = f * v * dx

# Решение задачи
u = Function(V)
solve(a == L, u, bcs)

#  Циркуляция 
n = FacetNormal(mesh)  
u_n = dot(grad(u), n)  
Gamma1 = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=5))
Gamma2 = assemble(u_n * ds(subdomain_data=boundaries, subdomain_id=6))
print(Gamma1, Gamma2)

c = plot(u, title="Решение")
plt.colorbar(c)
plt.show()
