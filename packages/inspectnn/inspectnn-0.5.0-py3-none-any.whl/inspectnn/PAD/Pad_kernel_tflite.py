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
def quant_3d_FakeMinMax(results, values,out_mul,out_offest,in_mul,in_offset):
    """
    Find the maximum value in values and store in result[0].
    Both result and values are 3d arrays.
    """
    #result_max = cuda.shared.array(shape=(10,10), dtype=int32)
    
    #TODO: valutare l' else 8risultato con matrice compresa con solo o 0 o val max
    i, j,k = cuda.grid(3)
    
    max_i=results.shape[0]
    max_j=results.shape[1]
    max_k=results.shape[2]
    
    
    d_i = (results.shape[0]-values.shape[0])/2
    d_j = (results.shape[1]-values.shape[1])/2
    
    
    #if the thread coordinates are outside of the image, we ignore the thread:
    if ((i >= max_i)  or (j >= max_j) or (k >= max_k)): 
        return

    #results[i,j,k] = round(values[i,j,k]*out_mul + out_offest)
    if i-d_i<0 or j-d_j<0 or i-d_i>=values.shape[0] or j-d_j>=values.shape[1] :
        results[i,j,k] = out_offest
    else:
        results[i,j,k] = values[i-d_i,j-d_j,k] #-in_offset)//in_mul*out_mul + out_offest)
    #results[i,j,k] = round(2**(quant_nbits+1)*(values[i,j,k]- 2**(quant_nbits)-t_min)/(t_max-2*t_min))#TODO:meno -1
    # CUDA conv kernel


@cuda.jit(cache=True)
def pad_3d(results, values,out_offest):
    i, j,k = cuda.grid(3)
    
    max_i=results.shape[0]
    max_j=results.shape[1]
    max_k=results.shape[2]
    
    #if the thread coordinates are outside of the image, we ignore the thread:
    if ((i >= max_i)  or (j >= max_j) or (k >= max_k)): 
        return
    
    d_i = (results.shape[0]-values.shape[0])//2
    d_j = (results.shape[1]-values.shape[1])//2
    
    #results[i,j,k] = round(values[i,j,k]*out_mul + out_offest)
    if i-d_i<0 or j-d_j<0 or i-d_i>=values.shape[0] or j-d_j>=values.shape[1] :
        results[i,j,k] = out_offest
    else:
        results[i,j,k] = values[i-d_i,j-d_j,k] #-in_offset)//in_mul*out_mul + out_offest)


@cuda.jit(cache=True)
def quant_2d(results, values,out_mul,out_offest,in_mul,in_offset):
    """
    Find the maximum value in values and store in result[0].
    Both result and values are 3d arrays.
    """

    i, j = cuda.grid(2)
    
    max_i=results.shape[0]
    max_j=results.shape[1]

    
    #if the thread coordinates are outside of the image, we ignore the thread:
    if ((i >= max_i)  or (j >= max_j) ): 
        return

    #TODO:fare un unico coeficente out_mul/in_mul
    results[i,j] = round((values[i,j]-in_offset)*out_mul/in_mul + out_offest)
    