from quad9 import quad9, quad9_post
from numpy import array, pi, zeros, ix_, around, unique, int32, arange, setdiff1d
from scipy.linalg import solve
import matplotlib.pylab as plt


fid = open("M1_Q9.msh","r")

LINE_ELEMENT = 8
QUAD_ELEMENT = 3
QUAD9_ELEMENT = 10

Empotrado = 1
BordeNatural = 2
Placa = 3
Extremos = 4

while True:
    line = fid.readline()

    if line.find("$Nodes")>=0:
        break

Nnodes = int(fid.readline())

xy = zeros([Nnodes,2])

for i in range(Nnodes):
    line = fid.readline()
    sl = line.split()
    xy[i,0] = float(sl[1])
    xy[i,1] = float(sl[2])

#print(f" xy = {xy}")
#print (f'Nnodes ={Nnodes}')

while True:
    line = fid.readline()
    if line.find("$Elements")>=0:
        break

Nelements = int(fid.readline())
#print (f'Nelements = {Nelements}')

conec = zeros((Nelements, 9), dtype = int32)

fixed_nodes = []
BordeNatural_nodes = []  #

Nquads= 0
Quadrangles = [] # Todos los quads

Extremos_Quads = [] # quads de los extremos t = 5 mm
Placa_Quads = [] # quads de la placa t = 4 mm

for i in range(Nelements):
    line = fid.readline()
    sl = line.split()
    element_number  =   int32(sl[0]) - 1
    element_type    =   int32(sl[1])
    physical_grp    =   int32(sl[3])
    entity_number   =   int32(sl[4])
    print(physical_grp)

    if element_type  == LINE_ELEMENT and physical_grp == Empotrado:
        n1 = int32(sl[5]) - 1
        n2 = int32(sl[6]) - 1
        n3 = int32(sl[7]) - 1
        fixed_nodes += [n1, n2, n3]

    if element_type  == LINE_ELEMENT and physical_grp == BordeNatural:
        n1 = int32(sl[5]) - 1
        n2 = int32(sl[6]) - 1
        n3 = int32(sl[7]) - 1
        BordeNatural_nodes += [n1, n2, n3]

    if element_type == QUAD9_ELEMENT and (physical_grp == Placa or physical_grp == Extremos):
        n0 = int32(sl[5]) - 1
        n1 = int32(sl[6]) - 1
        n2 = int32(sl[7]) - 1
        n3 = int32(sl[8]) - 1
        n4 = int32(sl[9]) - 1
        n5 = int32(sl[10]) - 1
        n6 = int32(sl[11]) - 1
        n7 = int32(sl[12]) - 1
        n8 = int32(sl[13]) - 1

        conec[element_number, :] = [n0, n1, n2, n3, n4, n5, n6, n7, n8]

        Quadrangles.append(element_number)
        Nquads += 1

        if physical_grp == Extremos:
            Extremos_Quads.append(element_number)

        if physical_grp == Placa:
            Placa_Quads.append(element_number)

#print (conec)
#print ("Fin del Archivo")
fid.close()

NDOFs = 2*Nnodes

rho = 2500
g = 9.81

# Props. placa:
properties_placa = {}
properties_placa["E"] = 20e9
properties_placa["nu"] = 0.25
properties_placa["bx"] = 0.0
properties_placa["by"] = 0.0
properties_placa["t"] = 4e-3 #4mm

#Props. extremos:
properties_extremo = {}
properties_extremo["E"] = 20e9
properties_extremo["nu"] = 0.25
properties_extremo["bx"] = 0.0
properties_extremo["by"] = 0.0
properties_extremo["t"] = 5e-3 #5mm

K = zeros((NDOFs, NDOFs))
f = zeros((NDOFs, 1))

for e in Quadrangles:
    ni = conec[e, 0]
    nj = conec[e, 1]
    nk = conec[e, 2]
    nl = conec[e, 3]
    nn = conec[e, 4]
    nm = conec[e, 5]
    no = conec[e, 6]
    np = conec[e, 7]
    nq = conec[e, 8]


    #print(f"e={e}   ni={ni}  nj={nj}   nk={nk}")

    xy_e = xy[[ni, nj, nk, nl, nn, nm, no, np, nq],:]

    if e in Placa_Quads:
        ke,fe = quad9(xy_e, properties_placa)

    if e in Extremos_Quads:
        ke,fe = quad9(xy_e, properties_extremo)

    d = [2*ni, 2*ni+1, 2*nj, 2*nj+1, 2*nk, 2*nk+1, 2*nl, 2*nl+1, 2*nn, 2*nn+1, 2*nm, 2*nm+1, 2*no, 2*no+1, 2*np, 2*np+1,  2*nq, 2*nq+1] # global DOFs from local dofs

    #Direct stiffnes method
    for i in range(18):
        p = d[i]
        for j in range(18):
            q = d[j]
            K[p,q] += ke[i,j]
        f[p] += fe[i]

fixed_nodes = unique(fixed_nodes)
constrained_DOFs = []

for n in fixed_nodes:
    constrained_DOFs += [2*n, 2*n+1]

free_DOFs = arange(NDOFs)
free_DOFs = setdiff1d(free_DOFs, constrained_DOFs)

#print(f"fixed_nodes = {fixed_nodes}")
#print(f"constrained_DOFs = {constrained_DOFs}")
#print(f"free_DOFS = {free_DOFs}")

#plt.matshow(K)
#plt.show()

#Nodal stress averaging
BordeNatural_nodes = unique(BordeNatural_nodes)
#print(BordeNatural_nodes)
border_quads = len(BordeNatural_nodes) - 1
#print(border_quads)

f[2*6] = 1000.0/(2*border_quads) #[N]
f[2*7] = 1000.0/(2*border_quads) #[N]

for n in BordeNatural_nodes:
    if n > 7 :
        f[2*n] = 1000.0/border_quads


Kff = K[ix_(free_DOFs, free_DOFs)]
Kfc = K[ix_(free_DOFs, constrained_DOFs)]
Kcf = K[ix_(constrained_DOFs, free_DOFs)]
Kcc = K[ix_(constrained_DOFs, constrained_DOFs)]

ff = f[free_DOFs]
fc = f[constrained_DOFs]

# Solve:
u = zeros((NDOFs, 1))
u[free_DOFs]= solve(Kff,ff)

# Get reaction forces:
R = Kcf @ u[free_DOFs] + Kcc @ u[constrained_DOFs] - fc

#print (f'u = {u}')
#print(f"R = {R}")


factor = 1e2
uv = u.reshape([-1,2])

#plt.plot(xy[:,0] + factor*uv[:,0], xy[:,1] + factor*uv[:,1],".")

for e in Quadrangles:
    ni = conec[e, 0]
    nj = conec[e, 1]
    nk = conec[e, 2]
    nl = conec[e, 3]
    nn = conec[e, 4]
    nm = conec[e, 5]
    no = conec[e, 6]
    np = conec[e, 7]
    nq = conec[e, 8]

    xy_e = xy[[ni, nj, nk, nl, nn, nm, no, np, nq, ni], :] + factor*uv[[ni, nj, nk, nl, nn, nm, no, np, nq, ni], :]
    plt.plot(xy_e[:, 0], xy_e[:, 1], 'k')

plt.axis('equal')
plt.show()

from gmsh_post import write_node_data, write_node_data_2, write_element_data

nodes = arange(1,Nnodes+1)
write_node_data("ux.msh", nodes, uv[:,0], "Despl. X")
write_node_data("uy.msh", nodes, uv[:,1], "Despl. Y")
write_node_data_2("desplazamientos.msh" , nodes, uv[:,0],uv[:,1] , "Despl")


#Calculo de tensiones

sigma_xx = zeros(len(Quadrangles)+1)
sigma_yy = zeros(len(Quadrangles)+1)
sigma_xy = zeros(len(Quadrangles)+1)

i=0

for e in Quadrangles:
    ni = conec[e, 0]
    nj = conec[e, 1]
    nk = conec[e, 2]
    nl = conec[e, 3]
    nn = conec[e, 4]
    nm = conec[e, 5]
    no = conec[e, 6]
    np = conec[e, 7]
    nq = conec[e, 8]

    xy_e = xy[[ni, nj, nk, nl, nn, nm, no, np, nq],:]

    uv_e= uv[[ni, nj, nk, nl, nn, nm, no, np, nq],:]

    u_e= uv_e.reshape((-1))

    if e in Placa_Quads:
        epsilon_e, sigma_e = quad9_post(xy_e, u_e, properties_placa)

    if e in Extremos_Quads:
        epsilon_e, sigma_e = quad9_post(xy_e, u_e, properties_extremo)

    sigma_xx[i] = sigma_e[0]
    sigma_yy[i] = sigma_e[1]
    sigma_xy[i] = sigma_e[2]

    i+=1

elementos = array(Quadrangles) + 1

write_element_data("sx.msh", elementos, sigma_xx , "Sigma_x" )
plt.close()
