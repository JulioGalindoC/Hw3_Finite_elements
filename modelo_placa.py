import numpy as np
from quad4 import quad4, quad4_post
from numpy import array, pi, zeros, ix_,around

fid = open("M1.msh","r")

LINE_ELEMENT = 1
TRI_ELEMENT  = 2
QUAD_ELEMENT = 3 

Empotrado = 1
BordeNatural = 2
Placa = 3 
Extremos = 4

while True:
    line = fid.readline()
    
    if line.find("$Nodes")>=0:
        break

Nnodes = int(fid.readline())

xy = np.zeros([Nnodes,2])

for i in range(Nnodes):
    line = fid.readline() 
    sl = line.split()
    xy[i,0] = float(sl[1])
    xy[i,1] = float(sl[2])

print (f' xy = {xy}')
print (f'Nnodes ={Nnodes}')

while True:
    line = fid.readline()
    if line.find("$Elements")>=0:
        break

Nelements = int(fid.readline())  
print (f'Nelements = {Nelements}')

conec = np.zeros((Nelements,4), dtype=np.int32)

fixed_nodes = []
BordeNatural_nodes = []

Nquads= 0
Quadrangles = []

Extremos_Quad = []
Placa_Quad = []
for i in range(Nelements):
    line = fid.readline() 
    sl = line.split()
    element_number  =   np.int32(sl[0]) -1 
    element_type    =   np.int32(sl[1])
    physical_grp    =   np.int32(sl[3])
    entity_number   =   np.int32(sl[4])

    if element_type  == LINE_ELEMENT and physical_grp == Empotrado: 
        n1 = np.int32(sl[5]) - 1 
        n2 = np.int32(sl[6]) - 1 
        fixed_nodes += [n1, n2]
        
    if element_type  == LINE_ELEMENT and physical_grp == BordeNatural:
        n1 = np.int32(sl[5]) - 1 
        n2 = np.int32(sl[6]) - 1 
        BordeNatural_nodes += [n1, n2]
    
    if element_type == QUAD_ELEMENT and (physical_grp == Placa or physical_grp == Extremos): 
        n0 = np.int32(sl[5]) - 1
        n1 = np.int32(sl[6]) - 1
        n2 = np.int32(sl[7]) - 1
        n3 = np.int32(sl[8]) - 1

        conec[element_number, :] = [n0, n1, n2, n3]

        Quadrangles.append(element_number)
        Nquads += 1 
        
        if physical_grp == Extremos:
            Extremos_Quad.append(element_number)
            
        if physical_grp == Placa:
            Placa_Quad.append(element_number)
            
print (conec)
print ("Fin del Archivo")

NDOFs = 2*Nnodes

properties = {}

rho = 2500
g = 9.81

# Props. placa:
properties_placa = {}
properties_placa["E"] = 20e9
properties_placa["nu"] = 0.25
properties_placa["bx"] = 0
properties_placa["by"] = 0
properties_placa["t"] = 4e-3 #4mm

#Props. extremos:
properties_extremo = {}
properties_extremo["E"] = 20e9
properties_extremo["nu"] = 0.25
properties_extremo["bx"] = 0
properties_extremo["by"] = 0
properties_extremo["t"] = 5e-3 #5mm

K = zeros((NDOFs, NDOFs))
f = zeros((NDOFs, 1))

for e in Quadrangles:
    ni = conec[e,0]
    nj = conec[e,1]
    nk = conec[e,2]
    nl = conec[e,3]
    
    print(f"e={e}   ni={ni}  nj={nj}   nk={nk}")

    xy_e = xy[[ni,nj,nk, nl],:]

    if e in Placa_Quad:
        ke,fe = quad4(xy_e,properties_placa)
        
    if e in Extremos_Quad:
        ke,fe = quad4(xy_e,properties_extremo)
        
    d = [2*ni, 2*ni+1 ,2*nj, 2*nj+1 ,2*nk , 2*nk+1,2*nl , 2*nl+1] # global DOFs from local dofs

    #Direct stiffnes method
    for i in range(8):
        p = d[i]
        for j in range(8):
            q = d[j]
            K[p,q] += ke[i,j]
        f[p] += fe[i]

fixed_nodes = np.unique(fixed_nodes)

constrained_DOFs = []
for n in fixed_nodes:
    constrained_DOFs += [2*n, 2*n +1]

print(f"fixed_nodes = {fixed_nodes}")   
print(f"constrained_DOFs = {constrained_DOFs}")

free_DOFs = np.arange(NDOFs)
free_DOFs = np.setdiff1d(free_DOFs,constrained_DOFs) 
print(f"free_DOFS = {free_DOFs}")

import matplotlib.pylab as plt

plt.matshow(K)
plt.show()

#Manualmente agregar cargas
BordeNatural_nodes = np.unique(BordeNatural_nodes)
for n in BordeNatural_nodes:
    f[2*n]=1000.0 # [N]

Kff = K[ix_(free_DOFs, free_DOFs)]
Kfc = K[ix_(free_DOFs, constrained_DOFs)]
Kcf = K[ix_(constrained_DOFs, free_DOFs)]
Kcc = K[ix_(constrained_DOFs, constrained_DOFs)]

ff = f[free_DOFs]
fc = f[constrained_DOFs]

# Solve:
from scipy.linalg import solve
u = zeros((NDOFs,1))

u[free_DOFs]=solve(Kff,ff)

# Get reaction forces:
R = Kcf @ u[free_DOFs] + Kcc @ u[constrained_DOFs] - fc

print (f'u = {u}')
print(f"R = {R}")

import matplotlib.pylab as plt
factor = 1e4
uv = u.reshape([-1,2])

plt.plot(xy[:,0] + factor*uv[:,0], xy[:,1] + factor*uv[:,1],".")

for e in Quadrangles:
    ni = conec[e,0]
    nj = conec[e,1]
    nk = conec[e,2]
    nl = conec[e,3]
    
    xy_e = xy[[ni, nj, nk,nl, ni],:] + factor*uv[[ni, nj, nk, nl, ni],:]
    plt.plot(xy_e[:,0], xy_e[:,1], 'k')

plt.axis('equal')
plt.show()

from gmsh_post import write_node_data_2,write_element_data

nodes = np.arange(1,Nnodes+1)
#write_node_data("ux.msh", nodes, uv[:,0], "Despl. X")
#write_node_data("uy.msh", nodes, uv[:,1], "Despl. Y")
write_node_data_2("desplazamientos.msh" , nodes, uv[:,0],uv[:,1] , "Despl")


#Calculo de tensiones

sigma_xx = np.zeros(Nquads+1)
sigma_yy = np.zeros(Nquads+1)
sigma_xy = np.zeros(Nquads+1)


i=0
for e in Quadrangles:
    ni = conec[e,0]
    nj = conec[e,1]
    nk = conec[e,2]
    nl = conec[e,3]
    
    xy_e= xy[[ni, nj, nk, nl, ni],:]

    uv_e= uv[[ni, nj, nk, nl],:] 

    u_e= uv_e.reshape((-1))

    if e in Placa_Quad:
        epsilon_e, sigma_e = quad4_post(xy_e, u_e, properties_placa)
        
    if e in Extremos_Quad:
        epsilon_e, sigma_e = quad4_post(xy_e, u_e, properties_extremo)
    
    sigma_xx[i] = sigma_e[0]
    sigma_yy[i] = sigma_e[1]
    sigma_xy[i] = sigma_e[2]
    
    i+=1 

elementos = np.array(Quadrangles) +1 

write_element_data("sx.msh", elementos, sigma_xx , "Sigma_x" )
