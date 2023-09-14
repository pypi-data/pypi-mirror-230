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
from inspectnn.GPU_kernel.Pool_kernel import pool

class DequantizateLayer(BaseLayer):
    def __init__(self, stride = (1, 1), pool_size = (2, 2), pooling = "max", name = "layer", input_memory = None):
        super().__init__(self, name = name)
        self.stride = stride
        self.pool_size = pool_size
        self.pool = pooling

    def __deepcopy__(self, memo = None):
        return DequantizateLayer(stride = self.stride, pool_size = self.pool_size, pooling = self.pool, name = self.name)

    def forward_pass(self, **kwargs):
        if self.gpu_input_memory is None:
            inputv = kwargs["inputv"]
            A_global_mem = cuda.to_device(np.array(inputv))
        else:
            A_global_mem=self.gpu_input_memory
        pool[self.griddim, self.blockdim](self.results, A_global_mem,self.stride_global_mem, self.pool_size_global_mem)#, pooling)
        if self.gpu_output_memory == False:
            cuda.synchronize()
            self.outputv[:,:,:] =self.results.copy_to_host()
            return self.outputv
        cuda.synchronize()

    def load_weights(self, **kwargs):
        self.input_shape, self.enable_gpu = kwargs["input_shape"],kwargs["enable_gpu"] 
        self.output_shape = [int(np.floor((self.input_shape[i] - self.pool_size[i]) / self.stride[i]) + 1) for i in range(2)] + [self.input_shape[2]]      
        self.outputv = np.zeros(self.output_shape)
        if self.enable_gpu:
            self.blockdim = (1,1,2)
            self.griddim = (self.output_shape[0] // self.blockdim[0] + 1, self.output_shape[1] // self.blockdim[1] + 1,self.output_shape[2] // self.blockdim[2] + 1)#,n_channels)
            self.use_gpu=True

            self.results = cuda.device_array(self.output_shape, dtype=np.int32)
            self.stride_global_mem = cuda.to_device(self.stride)
            self.pool_size_global_mem = cuda.to_device(self.pool_size)
            self.gpu_input_memory = kwargs["gpu_input_memory"]
        return self.output_shape
    