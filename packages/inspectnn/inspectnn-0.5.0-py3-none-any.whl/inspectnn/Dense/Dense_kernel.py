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
def F_activation(result,activation):
    if activation and result<0:
            return 0
    return result


#CUDA prodotto matriciale kernel
@cuda.jit
def matmul(R,A, B,bias, M,offset1,offset2,activation,quant_nbits,result_max):
    """
    Perform matrix di multiplication of C = A * B
    """
    row, col = cuda.grid(2)
    if row < R.shape[0] and col < R.shape[1]:
        tmp = bias[row]#TODO: rendere bias[row,col]    
        for k in range(A.shape[1]):
            tmp +=  M[int8(A[row, k])+offset1 , B[k, col]+offset2]   
        tmp=F_activation(tmp,activation)
        result_max[row, col] = 0
        R[row, col] = tmp
        

@cuda.jit
def max_2d(values,tmp):
    """
    Find the maximum value in values and store in result[0].
    Both result and values are 3d arrays.
    """

    i, j = cuda.grid(2)
    
    max_x=values.shape[0]
    max_y=values.shape[1]
    
    #if the thread coordinates are outside of the image, we ignore the thread:
    if ((i >= max_x)  or (j >= max_y) or values[i, j] == 0): 
        return
    
    cuda.atomic.max(tmp, (0, 1), values[i, j])

@cuda.jit
def quant_2d(results, values,tmp,quant_nbits):
    """
    Find the maximum value in values and store in result[0].
    Both result and values are 3d arrays.
    """
    if(tmp[0,1] <= 1):
        return

    i, j = cuda.grid(2) 
    max_x=results.shape[0]
    max_y=results.shape[1]
    #if the thread coordinates are outside of the image, we ignore the thread:
    if ((i >= max_x)  or (j >= max_y)): 
        return
    
    results[i,j] = round(( values[i,j]/tmp[0,1])*(2**quant_nbits-1))
    
    