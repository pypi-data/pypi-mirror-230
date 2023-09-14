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
from inspectnn.Add.Add_kernel_tflite import add3d_tflite,add3dv2_tflite

from scipy.special import softmax

class SoftmaxLayer(BaseLayer):
    def __init__(self, name = "cocatenate",activation = ""):
        super().__init__(self, name = name)
        self.activation = activation

    def __deepcopy__(self, memo = None):
        return SoftmaxLayer(name = self.name)

    def load_weights(self, **kwargs):
        self.input_shape= kwargs["input_shape"]
        self.output_shape = kwargs["output_shape"]
        self.outputv = np.zeros(self.output_shape)
        self.output_mul= 1/kwargs["quant_output_k"]
        self.output_offset= kwargs["quant_output_offset"]

    def forward_pass(self, inputv):
        self.outputv = softmax(inputv/self.pre_layer.output_mul + self.pre_layer.output_offset) #TODO: controllare se è la stessa softmax di tfLITE 
            

        