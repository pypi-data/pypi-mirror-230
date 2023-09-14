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
from numba import cuda, int8, int32
import time
TPB=16 #TODO:calcolare il tpb dinamicamente   

@cuda.jit(cache=True)
def pool(R, inputv, stride, pool_size,k_p):#, pooling):
    x, y,k = cuda.grid(3)
    if x < R.shape[0] and y < R.shape[1] and k*k_p < R.shape[2]:
        x_start = x * stride[0]
        x_end = min(x_start + pool_size[0],inputv.shape[0])
        y_start = y * stride[1]
        y_end = min(y_start + pool_size[1],inputv.shape[1])
        
        temp_max = cuda.local.array(shape=(16), dtype=int32)
        
        k = k * k_p
        k_max = min(R.shape[2],k+k_p)
        for p in range (k,k_max):
            temp_max[p-k]=-90000
            
        for i in range(x_start,x_end):
            for j in range(y_start,y_end):
                #for p in range (k,k_max):
                idp= 0
                for p in range (k,k_max):
                    
                    temp_max[idp]=max(inputv[i,j,p],temp_max[idp])
                    idp+=1
                        
        for p in range (k,k_max):                
            R[x, y, p] = temp_max[p-k]
    


#TODO: gestire il padding del pool avg
@cuda.jit(cache=True)
def pool_avg(R, inputv, stride, pool_size,k_p):#, pooling):
    x, y,k = cuda.grid(3)
    if x < R.shape[0] and y < R.shape[1] and k*k_p < R.shape[2]:
        x_start = x * stride[0]
        x_end = x_start + pool_size[0]
        y_start = y * stride[1]
        y_end = y_start + pool_size[1]
        temp_sum = cuda.local.array(shape=(16), dtype=int32)
        #temp_sum = 0
        k = k * k_p
        k_max = min(R.shape[2],k+k_p)
        for p in range (k,k_max):
            temp_sum[p-k]=0
            for i in range(x_start,x_end):
                for j in range(y_start,y_end):
                    
                    temp_sum[p-k]+=inputv[i,j,p]
        
            R[x, y, p] = round(temp_sum[p-k]/(pool_size[0]*pool_size[1]))
        
        
        
 