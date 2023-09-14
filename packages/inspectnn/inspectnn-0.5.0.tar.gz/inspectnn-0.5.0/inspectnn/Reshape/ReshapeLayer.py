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
from numba import cuda, jit
from inspectnn.BaseLayer import BaseLayer
from inspectnn.Reshape.Reshape_kernel_tflite import reshape_3d

class ReshapeLayer(BaseLayer):
    def __init__(self, name = "Reshape",dim_size = [1,1]):
        #TODO: Fare meglioo l' init
        super().__init__(self, name = name)
        self.dim_reshape = dim_size
        
    def __deepcopy__(self, memo = None):
        return ReshapeLayer(name = self.name,dim_size=self.dim_reshape)
    
    def load_weights(self, **kwargs):
        
        self.input_shape, self.enable_gpu = kwargs["input_shape"],kwargs["enable_gpu"] 
        self.output_shape = kwargs["output_shape"]      
        
        if self.enable_gpu:
            self.use_gpu=True

            
            self.use_3d = True
            self.blockdim = (2,2,2)
            self.griddim = (self.input_shape[0] // self.blockdim[0] + 1, self.input_shape[1] // self.blockdim[1] + 1,self.input_shape[2] // self.blockdim[2] + 1)#,n_channels)
        

            self.results = cuda.device_array(self.output_shape, dtype=np.int32)#int16 o 8
            
            self.dim_reshape_gpu = cuda.to_device(np.ascontiguousarray(self.dim_reshape))
            self.gpu_input_memory = kwargs["gpu_input_memory"]
            self.output_mul= 1/kwargs["quant_output_k"]
            self.output_offset= kwargs["quant_output_offset"]

        return self.output_shape
    
    #@jit
    def forward_pass(self):
        if self.gpu_input_memory is None:
            print("flat no buoeno")
            
        else:
            # TODO reshape su GPU
            cuda.synchronize()
            reshape_3d[self.griddim, self.blockdim](self.results, self.gpu_input_memory,self.dim_reshape_gpu)
            
            #print(self.name,"out",self.results.copy_to_host()[4][4])
            
            
 

        