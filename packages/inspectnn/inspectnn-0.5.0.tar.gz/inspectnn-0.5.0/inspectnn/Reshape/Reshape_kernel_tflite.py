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
from numba import cuda, int8


@cuda.jit(cache=True)
def reshape_3d(results, values,size):
    i, j,k = cuda.grid(3)
    
    max_i=values.shape[0]
    max_j=values.shape[1]
    max_k=values.shape[2]

    
    #if the thread coordinates are outside of the image, we ignore the thread:
    if ((i >= max_i)  or (j >= max_j) or (k >= max_k)): 
        return
    
    init_i = i*size[0]
    init_j = j*size[1]
    
    for ii in range(init_i,init_i+size[0]):
        for jj in range(init_j,init_j+size[1]):
            
            results[ii,jj,k] = values[i,j,k]


