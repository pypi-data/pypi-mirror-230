"""
Copyright 2022  Salvatore Barone <salvatore.barone@unina.it>
                Filippo Ferrandino <fi.ferrandino@studenti.unina.it>

This is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or any later version.

This is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
RMEncoder; if not, write to the Free Software Foundation, Inc., 51 Franklin
Street, Fifth Floor, Boston, MA 02110-1301, USA.
"""
from numba import cuda

@cuda.jit(cache=True)   
def add3d_tflite(result,a,b,k_a,k_b,off_a,off_b,activation,out_mul,out_offest):

    x, y,z= cuda.grid(3) 
    
    max_x=result.shape[0]
    max_y=result.shape[1]
    max_z=result.shape[2]

    if ((x >= max_x)  or (y >= max_y) or (z >= max_z)): 
        return 
    a1 = (a[x,y,z] - off_a)*k_a
    b1 = (b[x,y,z] - off_b)*k_b
    ris = a1 + b1

    if activation and ris<0:
        ris =0

    result[x,y,z] = round(ris*out_mul + out_offest)

@cuda.jit(cache=True) 
def add3dv2_tflite(result,a,b,k_a,k_b,off_a,off_b,activation,out_mul,out_offest):

    x, y= cuda.grid(2) 
    
    max_x=result.shape[0]
    max_y=result.shape[1]
    max_z=result.shape[2]

    if ((x >= max_x)  or (y >= max_y)): 
        return 
    for z in range(max_z):
        a1 = (a[x,y,z] - off_a)*k_a
        b1 = (b[x,y,z] - off_b)*k_b
        ris = a1 + b1

        if activation and ris<0:
            ris =0

        result[x,y,z] = round(ris*out_mul + out_offest)

