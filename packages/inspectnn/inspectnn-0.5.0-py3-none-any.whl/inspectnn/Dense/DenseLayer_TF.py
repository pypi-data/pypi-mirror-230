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
from inspectnn.Dense.Dense_kernel import matmul, quant_2d,    max_2d
from inspectnn.Dense.DenseLayer import DenseLayer       

class DenseLayer_TF(DenseLayer):
    def __init__(self, activation = "relu", quant_nbits = 8, multiplier = BaseLayer.default_multiplier, name = "layer",offset=[128,128],print_output=None):
        super().__init__( activation, quant_nbits, multiplier, name,offset,print_output)

    def __deepcopy__(self, memo = None):
        return DenseLayer_TF(activation = self.activation, quant_nbits = self.quant_nbits, multiplier = self.multiplier, name = self.name)

    def forward_pass(self, **kwargs):
        # TODO Aggiungi supporto per altre attivazioni
        activation = self.activation == "relu"

        if self.gpu_input_memory is None:
            inputv = kwargs["inputv"]
            #print("dense no buoeno")
            A_global_mem = cuda.to_device(np.array(inputv))
        else:
            A_global_mem= self.pre_layer.results

        cuda.synchronize()
        matmul[self.griddim, self.blockdim](self.results_mul, A_global_mem,self.weights,self.biases,self.M,128,128,activation,self.quant_nbits,self.results_max)#offset1,offset2)
        
        cuda.synchronize()
        
        #TODO: ottimizare questo schifo di if (è tempo di portare la softmax sulla gpu?- no, non la faccio proprio)
        if "softmax"!=self.activation:
            max_2d[self.griddim, self.blockdim](self.results_mul,self.results_max)
            cuda.synchronize()
            quant_2d[self.griddim, self.blockdim](self.results, self.results_mul,self.results_max,self.quant_nbits)
            cuda.synchronize()
        
        if self.gpu_output_memory == False:
            #print("Dense out")
            if "softmax"!=self.activation:
                self.outputv[:,:] = self.results.copy_to_host()
            else:
                self.outputv[:,:] = self.results_mul.copy_to_host()
        if self.activation == "softmax":
            if self.activation is not None:
                self.outputv = BaseLayer.activations[self.activation](self.outputv)
            if self.quant_nbits is not None:
                self.outputv = np.round((self.outputv/np.max(self.outputv))*(2**self.quant_nbits-1))
            return self.outputv

    def load_weights(self, **kwargs):
        super().load_weights(**kwargs)
        return self.output_shape
   
    
