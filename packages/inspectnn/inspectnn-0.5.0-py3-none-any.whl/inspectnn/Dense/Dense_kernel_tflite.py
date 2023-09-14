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
from numba import cuda, int8,int16,int32

@cuda.jit(cache=True)
def matmul_tflite(R,A, B,k_mul,k_filtri,k_bias, M,offset1,offset2,activation,out_mul,out_offest,update_bias):

    #MM = cuda.shared.array((128,128),dtype = int16)
    
    #for i in range(128):
    #    for j in range(128):
    #        MM[i,j] = M[i,j]
            
    row, col = cuda.grid(2)
    if row < R.shape[0] and col < R.shape[1]:
        tmp = 0
        for k in range(A.shape[1]): 
            tmp +=  M[int8(A[row, k])+offset1 , int8(B[col, k]+offset2)]        
            #tmp += A[row, k]*B[col, k]
            
        #ris = k_mul[row]*tmp - k_filtri[col] + k_bias[col]#TODO:in caso di moltiplicazione matriciali(questa di fatto è un vettore per una matrice è)
        ris = k_mul[row]*tmp - k_filtri[col] + k_bias[col] + update_bias[col]
        
        if activation and ris<0:
            ris=0

        R[row, col] = round(ris*out_mul + out_offest)
        
    return   

@cuda.jit(cache=True)
def matmul_tflite_occorenza(R,A, B,k_mul,k_filtri,k_bias, M,offset1,offset2,activation,out_mul,out_offest,occorenza):
    
    row, col = cuda.grid(2)
    if row < R.shape[0] and col < R.shape[1]:
        tmp = 0
        for k in range(A.shape[1]): 
            tmp +=  M[int8(A[row, k])+offset1 , int8(B[col, k]+offset2)]
            occorenza[col,int8(A[row, k])+offset1 , int8(B[col, k]+offset2)] += 1
            #tmp += A[row, k]*B[col, k]
            
        ris = k_mul[row]*tmp - k_filtri[col] + k_bias[col]#TODO:in caso di moltiplicazione matriciali(questa di fatto è un vettore per una matrice è)
        
        if activation and ris<0:
            ris=0

        R[row, col] = round(ris*out_mul + out_offest)
        
    return   

@cuda.jit(cache=True)
def matmul_tflite_mf(R,A, B,k_mul,k_filtri,k_bias, M,offset1,offset2,activation,out_mul,out_offest,idx_multiply):
    
    #MM = cuda.shared.array((128,128),dtype = int16)
    
    #for i in range(128):
    #    for j in range(128):
    #        MM[i,j] = M[i,j]
            
    row, col = cuda.grid(2)
    if row < R.shape[0] and col < R.shape[1]:
        tmp = 0
        for k in range(A.shape[1]):
            
            tmp +=  M[idx_multiply[col],int8(A[row, k])+offset1 , int8(B[col, k]+offset2)]
            
            #tmp += A[row, k]*B[col, k]
            
        ris = k_mul[row]*tmp - k_filtri[col] + k_bias[col]#TODO:in caso di moltiplicazione matriciali(questa di fatto è un vettore per una matrice è)
        
        if activation and ris<0:
            ris=0

        R[row, col] = round(ris*out_mul + out_offest)
        
    return   



TPB = 16
@cuda.jit(cache=True)
def fast_matmul_tflite(R,A, B,k_mul,k_filtri,k_bias, M,offset1,offset2,activation,out_mul,out_offest,update_bias):
    # Define an array in the shared memory
    # The size and type of the arrays must be known at compile time
    sA = cuda.shared.array(shape=(TPB, TPB), dtype=int32)
    sB = cuda.shared.array(shape=(TPB, TPB), dtype=int32)

    x, y = cuda.grid(2)

    tx = cuda.threadIdx.x
    ty = cuda.threadIdx.y
    bpg = cuda.gridDim.x    # blocks per grid

    if x >= R.shape[0] and y >= R.shape[1]:
        # Quit if (x, y) is outside of valid C boundary
        return

    # Each thread computes one element in the result matrix.
    # The dot product is chunked into dot products of TPB-long vectors.
    tmp = 0
    for i in range(bpg):
        # Preload data into shared memory
        sA[ty, tx] = 0
        sB[ty, tx] = 0
        if y < A.shape[0] and (tx + i * TPB) < A.shape[1]:
            sA[ty, tx] = A[y, tx + i * TPB]
        if x < B.shape[1] and (ty + i * TPB) < B.shape[0]:
            sB[ty, tx] = B[ty + i * TPB, x]
        # Wait until all threads finish preloading
        cuda.syncthreads()

        # Computes partial product on the shared memory
        for j in range(TPB):
            #tmp += M[int8(sA[tx, j] )+offset1 , int8(sB[j, ty]+offset2)]   
            tmp += sA[tx, j] * sB[j, ty]

        # Wait until all threads finish computing
        cuda.syncthreads()

    
    ris = k_mul[x]*tmp - k_filtri[y] + k_bias[y] + update_bias[y]
        
    if activation and ris<0:
        ris=0

    R[x, y] = round(ris*out_mul + out_offest)



max_segment = 1
@cuda.jit(cache=True)
def matmul_tflite_fast_pippo(R,A, B,k_mul,k_filtri,k_bias, M,offset1,offset2,activation,out_mul,out_offest,update_bias):

    #MM = cuda.shared.array((128,128),dtype = int16)
    
    #for i in range(128):
    #    for j in range(128):
    #        MM[i,j] = M[i,j]
    
    row , col,segment = cuda.grid(3)

    tmp_shared = cuda.shared.array(shape=(max_segment), dtype=int32)
    if row < R.shape[0] and col < R.shape[1] and segment < max_segment:
        tmp = 0
        #segment = 0
        for k in range(segment*A.shape[1]//max_segment,(1+segment)*A.shape[1]//max_segment): 
            tmp_shared[segment] +=  M[int8(A[row, k])+offset1 , int8(B[col, k]+offset2)]        
            #tmp += A[row, k]*B[col, k]
            
        cuda.syncthreads()
        if segment == 0:
            for i in range(max_segment):
                tmp += tmp_shared[i]
        #ris = k_mul[row]*tmp - k_filtri[col] + k_bias[col]#TODO:in caso di moltiplicazione matriciali(questa di fatto è un vettore per una matrice è)
        
            ris = k_mul[row]*tmp - k_filtri[col] + k_bias[col] + update_bias[col]
        
            if activation and ris<0:
                ris=0
                
                
            R[row, col] =round(ris*out_mul + out_offest)
    return   