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
from inspectnn.Conv.Conv_kernel import convolve,quant_3d,max_3d
from inspectnn.Conv.ConvLayer import ConvLayer
class ConvLayer_TF(ConvLayer):
    def __init__(self, stride = (1, 1), padding = (0,0), activation = "relu", quant_nbits = 8, multiplier = BaseLayer.default_multiplier, name = "layer",offset=[128,128],print_output=None):
        super().__init__( stride, padding,activation,quant_nbits,multiplier,name,offset,print_output)
   
    def __deepcopy__(self, memo = None):
        return ConvLayer_TF(stride = self.stride, padding = self.padding, activation = self.activation, quant_nbits = self.quant_nbits, multiplier = self.multiplier, name = self.name)

    def forward_pass(self, **kwargs):
        #TODO: rinominare variabili
        if self.gpu_input_memory is None:
            inputv = kwargs["inputv"]
            A_global_mem = cuda.to_device(np.array(inputv))
        else:
            A_global_mem = self.gpu_input_memory 
        #TODO: rinominare M
        convolve[self.griddim, self.blockdim](self.results_conv,A_global_mem,self.kernel_global_mem,self.biases,self.n_channels,self.M,128,128,self.quant_nbits,self.results_max)
        cuda.synchronize()
        #TODO: calcolare grid_dim per quant 3d
        max_3d[self.quant_griddim, self.quant_blockdim](self.results_conv,self.results_max)

        cuda.synchronize()

        quant_3d[self.quant_griddim, self.quant_blockdim](self.results, self.results_conv,self.results_max,self.quant_nbits)

        cuda.synchronize()
        if self.gpu_output_memory == False:
            self.outputv[:,:,:] = self.results.copy_to_host()
            return self.outputv
  
    def load_weights(self, **kwargs):
        super().load_weights(**kwargs)
                 
        return self.output_shape
  