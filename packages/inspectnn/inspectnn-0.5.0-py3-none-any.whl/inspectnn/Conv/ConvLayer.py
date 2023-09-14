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
from numba import cuda
from inspectnn.BaseLayer import BaseLayer

class ConvLayer(BaseLayer):
    def __init__(self, stride = (1, 1), padding = (0,0), activation = "relu", quant_nbits = 8, multiplier = BaseLayer.default_multiplier, name = "Conv_Base",offset=[128,128],print_output=None):
        super().__init__(activation, quant_nbits, multiplier, name,print_output)
        self.stride = stride
        self.padding = padding
        self.kernel_global_mem = None
        self.M = None
        self.offset = offset
        
    def __deepcopy__(self, memo = None):
        return ConvLayer(stride = self.stride, padding = self.padding, activation = self.activation, quant_nbits = self.quant_nbits, multiplier = self.multiplier, name = self.name)

    def forward_pass(self, **kwargs):
        return None
  
    def load_weights(self, **kwargs):
        self.enable_gpu = kwargs["enable_gpu"] 
        self.input_shape= kwargs["input_shape"]
        self.kernel_shape = np.shape(kwargs["weights"])   
   
        self.output_shape = [int(np.floor((self.input_shape[i] - self.kernel_shape[i] + 2 * self.padding[i]) / self.stride[i] + 1)) for i in range(2)] + [self.kernel_shape[3]]
        self.blockdim = (2,2,2)
        self.griddim = (self.input_shape[0] // self.blockdim[0] + 1, self.input_shape[1] // self.blockdim[1] + 1)#,n_channels)
        self.n_channels=self.kernel_shape[3]

        if self.enable_gpu:
            self.use_gpu=True
            self.M = self.multiplier
            self.blockdim = (2,2,2)
            self.griddim = (self.input_shape[0] // self.blockdim[0] + 1, self.input_shape[1] // self.blockdim[1] + 1,self.output_shape[2] // self.blockdim[2] + 1)#,n_channels)
            self.quant_blockdim = (2,2,2)
            self.quant_griddim = (self.output_shape[0] // self.quant_blockdim[0] + 1, self.output_shape[1] // self.quant_blockdim[1] + 1,self.output_shape[2] // self.quant_blockdim[2] + 1)#,n_channels)
            self.kernel_global_mem = cuda.to_device(np.array(kwargs["weights"],dtype=np.int32))
            self.biases = cuda.to_device(np.array(kwargs["biases"],dtype=np.int16))
            self.results = cuda.device_array(self.output_shape, dtype=np.int32)
            self.results_max = cuda.to_device(np.zeros(self.output_shape, dtype=np.int32))
            self.results_conv = cuda.device_array(self.output_shape,  dtype=np.int32)
            
            self.gpu_input_memory = kwargs["gpu_input_memory"]  
            print(self.name,'bias:',np.array(kwargs["weights"].shape))

            if self.print_output:
                self.outputv = np.zeros(self.output_shape)              
        else:
            self.convkernel, self.biases =kwargs["weights"], kwargs["biases"]
            self.outputv = np.zeros(self.output_shape)
            print(self.name,'No gpu !!!!')
         
        if None == self.gpu_input_memory:
                self.outputv = np.zeros(self.output_shape)          
        return self.output_shape
  