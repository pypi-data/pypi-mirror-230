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

       
class DenseLayer(BaseLayer):
    def __init__(self, activation = "relu", quant_nbits = 8, multiplier = BaseLayer.default_multiplier, name = "layer",offset=[128,128],print_output=None):
        super().__init__( activation, quant_nbits, multiplier, name,print_output)
        self.offset=offset

    def __deepcopy__(self, memo = None):
        return DenseLayer(activation = self.activation, quant_nbits = self.quant_nbits, multiplier = self.multiplier, name = self.name)

    def forward_pass(self, **kwargs):
        return None


    def load_weights(self, **kwargs):
        self.enable_gpu = kwargs["enable_gpu"]
        self.input_shape = kwargs["input_shape"]
        self.weights, self.biases =kwargs["weights"], kwargs["biases"]
        self.output_shape = [self.input_shape[0], kwargs["weights"].shape[1]]     
        self.outputv = np.zeros(self.output_shape)
        self.blockdim = (1,8)
        self.griddim = (self.output_shape[0] // self.blockdim[0] + 1, self.output_shape[1] // self.blockdim[1] + 1)#,n_channels)
        if self.enable_gpu:
            self.use_gpu=True
            self.M = self.multiplier
            self.weights = cuda.to_device(np.array(self.weights,dtype=np.int16))
            self.biases = cuda.to_device(np.array(self.biases,dtype=np.int32))
            self.results = cuda.device_array(self.output_shape, dtype=np.int32)
            self.results_max = cuda.to_device(np.zeros(self.output_shape, dtype=np.int32))
            self.results_mul = cuda.device_array(self.output_shape, dtype=np.int32)
            self.gpu_input_memory = kwargs["gpu_input_memory"]
        if self.gpu_input_memory is None:
            self.outputv = np.zeros(self.output_shape)   
        return self.output_shape
   
    
