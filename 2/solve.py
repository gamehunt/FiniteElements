from fenics import *
import matplotlib.pyplot as plt

mesh = Mesh("mesh/5/grid_5.xml")
boundaries = MeshFunction("size_t", mesh, "mesh/5/grid_5_facet_region.xml")

ds = Measure("ds", subdomain_data=boundaries)

  
V = FunctionSpace(mesh, "CG", 2)

# Условие на входе в канал
u_1 = Expression("x[1]", degree=2)

# Граничные условия
bcs = [DirichletBC(V, Constant(0.0), boundaries, 1),
       DirichletBC(V, Constant(1.0), boundaries, 2),
       DirichletBC(V, Constant(0.5), boundaries, 5),
       DirichletBC(V, Constant(0.5), boundaries, 6),
       DirichletBC(V, u_1, boundaries, 3)]

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
