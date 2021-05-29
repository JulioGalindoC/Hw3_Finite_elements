# Hw3 Finite Elements Part 1
## Geometry
![Placa_geo](Placa_geo.png) 
## Mesh
![Placa](Placa.png) 
## Element displacement for different meshes
![disp1](Desp.png) 

![disp2](deformada.png) 

Al graficar los esfuerzos tuvimos problemas con Gmsh. Creemos que el codigo esta bien al recuperar sigmas y desplazamientos pero que cargarlo a Gmsh se produce un error.


# Hw3 Finite Elements Part 2
## Geometry
![Placa_geo](Placa_geo.png) 

## Coaerse Mesh

### Mesh:
![M1](Homework3_Part2/M1.png)
### Deformation plot with python: 
![M1_Pgraph](Homework3_Part2/M1_Pgraph.png)
### Displacements in Gmsh
![M1_desp](Homework3_Part2/M1_desp.png)
### Stress in Gmsh
![M1_sx](Homework3_Part2/M1_sx.png)

## Medium Mesh:

### Mesh:
![M2](Homework3_Part2/M2.png)
### Deformation plot with python: 
![M2_Pgraph](Homework3_Part2/M2_Pgraph.png)
### Displacements in Gmsh
![M2_desp](Homework3_Part2/M2_desp.png)
### Stress in Gmsh
![M2_sx](Homework3_Part2/M2_sx.png)

## Fine Mesh:

### Mesh:
![M3](Homework3_Part2/M3.png)
### Deformation plot with python:  
![M3_Pgraph](Homework3_Part2/M3_Pgraph.png)
### Displacements in Gmsh
![M3_desp](Homework3_Part2/M3_desp.png)
### Stress in Gmsh
![M3_sx](Homework3_Part2/M3_sx.png)


## Nodal Stress Averaging:

![Nodal_Stress_Averaging](Homework3_Part2/Nodal_Stress_Averaging.png)


The first step to accomplish this implementation was to generate a list, containing all the natural nodes.

Once we had this list, we calculate the number of elements in the natural border. If there are n nodes in the border, there will be n-1 elements in the same border. 

As we can see from the geometry, it is always  true that the right bottom node is node number 7, and the right top node is always number 8. Knowing this, we set the load of this nodes as F/(2·Number of elements).

Finally, the loads of all other natural boundary nodes are set with a for:
for n in BordeNatural_nodes:
    if n > 7 :
        f[2*n] = F/Number of elements

### Before Nodal Stress Averaging:
![antes](Homework3_Part2/antes.png)

### After Nodal Stress Averaging:
![despues](Homework3_Part2/despues.png)


# Hw3 Finite Elements Part 3
## Geometry
![Placa_geo](Placa_geo.png)

## Coaerse Mesh

### Mesh:
![Coarse_M](HW3_Part3/Coarse_Mesh/Coarse_M.png)
### Displacements in Gmsh
![Coarse_D](HW3_Part3/Coarse_Mesh/Coarse_D.png)
### Stress in Gmsh
![Coarse_S](HW3_Part3/Coarse_Mesh/Coarse_S.png)

## Medium Mesh:

### Mesh:
![Medium_M](HW3_Part3/Medium_Mesh/Medium_M.png)

### Displacements in Gmsh
![Medium_D](HW3_Part3/Medium_Mesh/Medium_D.png)
### Stress in Gmsh
![Medium_S](HW3_Part3/Medium_Mesh/Medium_S.png)

## Fine Mesh:

### Mesh:
![Fine_M](HW3_Part3/Fine_Mesh/Fine_M.png)

Advantages of using Quad9 elements is that we can describe the curved sides, while with Quad 4 elements it is not possible. Also, Quad9 elements behave with less stiffness than Quad4 elements, so it is very useful for Finite elements method.
