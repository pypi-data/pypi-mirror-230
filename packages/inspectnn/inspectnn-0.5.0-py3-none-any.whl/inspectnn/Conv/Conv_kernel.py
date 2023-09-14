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

@cuda.jit    
def convolve(result,a, b,bias,n_channels,M,offset1,offset2,quant_nbits,result_max):
    #coordinates of the current thread:
    
    x, y,p = cuda.grid(3) 
    max_x=a.shape[0]-b.shape[0]+1
    max_y=a.shape[1]-b.shape[1]+1
    #if the thread coordinates are outside of the image, we ignore the thread:
    if ((x >= max_x)  or (y >= max_y) or (p >=n_channels)): 
        return
 
    s=bias[p]    
            #calcolo cella convoluzione
            #todo: aggiungere lo step
    for i in range(b.shape[0]):
        for j in range(b.shape[1]):
            for k in range(a.shape[2]):
                s += M[int8(a[i+x,j+y,k])+offset1,b[i,j,k,p]+offset2]
    
    #activation rele
    if s<0:
        s=0
    result_max[x,y,p] = 0
    result[x,y,p] = s


@cuda.jit
def max_3d(values,tmp):
    i, j,k = cuda.grid(3)
    
    max_i=values.shape[0]
    max_j=values.shape[1]
    max_k=values.shape[2]
    
    #if the thread coordinates are outside of the image, we ignore the thread:
    if ((i >= max_i)  or (j >= max_j) or (k >= max_k) or values[i, j,k] == 0): 
        return
      
    # Atomically store to result[0,1,2] from values[i, j, k]
    cuda.atomic.max(tmp, (0, 1,2), values[i, j,k])

@cuda.jit
def quant_3d(results, values,tmp,quant_nbits):
    """
    Find the maximum value in values and store in result[0].
    Both result and values are 3d arrays.
    """

    if (tmp[0,1,2] <= 1):
        return
    #TODO: valutare l' else 8risultato con matrice compresa con solo o 0 o val max
    i, j,k = cuda.grid(3)
    
    max_i=results.shape[0]
    max_j=results.shape[1]
    max_k=results.shape[2]
    
    #if the thread coordinates are outside of the image, we ignore the thread:
    if ((i >= max_i)  or (j >= max_j) or (k >= max_k)): 
        return

   
    results[i,j,k] = round(( values[i,j,k]/tmp[0,1,2])*(2**quant_nbits-1))#TODO:meno -1
    
    # CUDA conv kernel
