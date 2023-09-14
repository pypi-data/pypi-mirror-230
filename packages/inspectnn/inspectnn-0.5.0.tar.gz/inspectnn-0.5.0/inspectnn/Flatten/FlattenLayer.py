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

class FlattenLayer(BaseLayer):
    def __init__(self, name = "layer"):
        super().__init__(self, name = name)

    def __deepcopy__(self, memo = None):
        return FlattenLayer(name = self.name)

    def load_weights(self, **kwargs):
        self.input_shape, self.enable_gpu = kwargs["input_shape"], kwargs["enable_gpu"] 
        self.output_shape = [1, np.prod(self.input_shape)]
        self.outputv = np.zeros(self.output_shape)
        if self.enable_gpu:
            self.use_gpu = True
            self.results = cuda.device_array(self.output_shape,dtype=np.int32)
            self.gpu_input_memory = kwargs["gpu_input_memory"]
        return self.output_shape
    
    #@jit
    def forward_pass(self):
        if self.gpu_input_memory is None:
            print("flat no buoeno")
            
        else:
            # TODO reshape su GPU
            cuda.synchronize()
            self.results = self.gpu_input_memory.reshape(self.output_shape[0],self.output_shape[1])#,order='A')#order='C' F A 
            
 

        