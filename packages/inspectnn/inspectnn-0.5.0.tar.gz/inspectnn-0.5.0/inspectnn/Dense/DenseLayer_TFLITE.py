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
import numpy as np
import time
from numba import cuda, jit
from inspectnn.BaseLayer import BaseLayer
from inspectnn.Dense.Dense_kernel_tflite import matmul_tflite,matmul_tflite_occorenza,matmul_tflite_mf,matmul_tflite_fast_pippo

from inspectnn.Dense.DenseLayer import DenseLayer

class DenseLayer_TFLITE(DenseLayer):
    def __init__(self, activation = "relu", quant_nbits = 8, multiplier = BaseLayer.default_multiplier, name = "layer",offset=[128,128],print_output=None):
        super().__init__( activation, quant_nbits, multiplier, name,print_output)
        self.offset=offset
        self.idx_multiply = None

    def __deepcopy__(self, memo = None):
        return DenseLayer_TFLITE(activation = self.activation, quant_nbits = self.quant_nbits, multiplier = self.multiplier, name = self.name)

    #@jit
    def forward_pass(self):
        # TODO Aggiungi supporto per altre attivazioni

        A_global_mem= self.pre_layer.results
 
        #print(self.name,"input",A_global_mem.copy_to_host()[0][:16])

        if(self.idx_multiply is None):
            cuda.synchronize()
            #matmul_tflite
            #fast_matmul_tflite
            #print([self.griddim, self.blockdim])
            matmul_tflite[self.griddim, self.blockdim](self.results, A_global_mem,self.weights,self.k_mul,self.k_filtri,self.k_bias,self.M,128,128,self.activation,self.output_mul,self.output_offset,self.update_bias)
        else:
            #print(self.name,self.idx_multiply)
            idxm = cuda.to_device(np.ascontiguousarray(self.idx_multiply))
            cuda.synchronize()
            matmul_tflite_mf[self.griddim, self.blockdim](self.results, A_global_mem,self.weights,self.k_mul,self.k_filtri,self.k_bias,self.all_M,128,128,self.activation,self.output_mul,self.output_offset,idxm)
    

        #print('ris_mul:',self.results.copy_to_host()[0])
        #TODO: ottimizare questo schifo di if (è tempo di portare la softmax sulla gpu?- ancora no)
    
        if self.gpu_output_memory == False:
            cuda.synchronize()
            self.outputv[:,:] = self.results.copy_to_host()
            
          

    def load_weights(self, **kwargs):
        self.enable_gpu = kwargs["enable_gpu"]
        self.input_shape = kwargs["input_shape"]
        self.weights_cpu=np.array(kwargs["weights"],dtype=np.int16)
        #self.weights=kwargs["weights"]
        self.output_shape = kwargs["output_shape"]  
        self.outputv = np.zeros(self.output_shape)
        self.blockdim = (1,8)
        self.n_filter = self.output_shape[1]
        self.griddim = (self.output_shape[0] // self.blockdim[0] + 1, self.output_shape[1] // self.blockdim[1] + 1)#,n_channels)
        if self.enable_gpu:
            self.use_gpu=True
            self.M = self.multiplier
            #todo accorciare
            self.weights = cuda.to_device(np.array(kwargs["weights"],dtype=np.int16))
            self.occorenza = cuda.to_device(np.zeros((self.n_filter,256,256),dtype=np.int32))
            self.results = cuda.device_array(self.output_shape, dtype=np.int32)         
            self.gpu_input_memory = kwargs["gpu_input_memory"]

            if ( kwargs["quant_data"] is not None):
                self.quantization=True
                self.quanto_bias = cuda.to_device(np.ascontiguousarray(kwargs["quant_bias"]))
                self.quanto_B = cuda.to_device(np.ascontiguousarray(kwargs["quant_data"]))
                
                self.update_bias = cuda.to_device(np.ascontiguousarray(np.zeros(self.n_filter)))
                self.k_mul = cuda.to_device(np.ascontiguousarray(kwargs["quant_data"]*kwargs["quant_input_k"]))#TODO:parametrizare il 255
                self.k_filtri = cuda.to_device(np.ascontiguousarray(np.sum(kwargs["weights"],(1))*kwargs["quant_data"]*kwargs["quant_input_offset"]*kwargs["quant_input_k"]))#TODO:parametrizare il diviso 2 con alfa input+offest input
                self.k_bias = cuda.to_device(np.ascontiguousarray(kwargs["biases"]*kwargs["quant_bias"]))

                self.output_mul= 1/kwargs["quant_output_k"]
                self.output_offset= kwargs["quant_output_offset"]

        self.activation = (self.activation == "relu" or self.activation == "Relu")
        if self.gpu_input_memory is None:
            self.outputv = np.zeros(self.output_shape)   
        return self.output_shape
   
    
    def research_hyperparameters(self):
        
        best_blockdim = self.blockdim
        best_griddim = self.griddim 
        best_time = 100000000
        for i in range(0,16):
            for j in range(0,16):
            
                self.blockdim = (i+1,j+1)
                self.griddim = (self.output_shape[0] // self.blockdim[0] + 1, self.output_shape[1] // self.blockdim[1] + 1)#,n_channels)
                init_time = time.time()
                
                for i in range(2):
                    self.forward_pass()
                    
                tot_time = time.time() - init_time
                #print("blockdim:",self.blockdim,"griddim:",self.griddim,"time:",tot_time)
                
                if tot_time < best_time:
                    best_blockdim = self.blockdim
                    best_griddim = self.griddim
                    best_time = tot_time
        
        print("best_blockdim:",best_blockdim,"best_griddim:",best_griddim)
        
        self.blockdim = best_blockdim
        self.griddim = best_griddim
        