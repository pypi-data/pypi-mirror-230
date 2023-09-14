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
from inspectnn.Somma.Add_kernel_tflite import add3d_tflite,add3dv2_tflite


class AddLayer(BaseLayer):
    def __init__(self, name = "cocatenate",activation = ""):
        super().__init__(self, name = name)
        self.activation = activation

    def __deepcopy__(self, memo = None):
        return AddLayer(name = self.name)

    def load_weights(self, **kwargs):
        self.input_shape_A,self.input_shape_B, self.enable_gpu = kwargs["input_shape_A"],kwargs["input_shape_B"], kwargs["enable_gpu"] 
        self.output_shape = kwargs["output_shape"]
        self.outputv = np.zeros(self.output_shape)

        self.blockdim = (1,1,1)
        self.griddim = (self.output_shape[0] // self.blockdim[0] + 1, self.output_shape[1] // self.blockdim[1] + 1,self.output_shape[2] // self.blockdim[2] + 1)#,n_channels)

        if self.enable_gpu:
            self.use_gpu = True
           
            self.results = cuda.device_array(self.output_shape, dtype=np.int32)
            self.gpu_layer_A = None
            self.gpu_layer_B = None

            self.output_K = kwargs["quant_output_k"]
            self.output_mul = 1/kwargs["quant_output_k"]
            self.output_offset = kwargs["quant_output_offset"]
        return self.output_shape
    
    def forward_pass(self, **kwargs):
        if self.gpu_layer_A is None:
            print("add no buoeno")

        else:

            activation = (self.activation == "relu" or self.activation == "Relu")

            add3d_tflite[self.griddim, self.blockdim](self.results,self.gpu_layer_A.results,self.gpu_layer_B.results,
                                                    self.A_mul,self.B_mul,
                                                    self.A_off,self.B_off,
                                                    activation,self.output_mul,self.output_offset)

            cuda.synchronize()
            

    def load_input_layer(self,layers,tensors_out):
        op_in1=self.code_tensor_inputs[0]
        op_in2=self.code_tensor_inputs[1]

        self.gpu_layer_A = layers[tensors_out.index(op_in1)]
        self.gpu_layer_B = layers[tensors_out.index(op_in2)]

        self.gpu_output_memory = True

        self.A_mul=1/self.gpu_layer_A.output_mul
        self.B_mul=1/self.gpu_layer_B.output_mul

        self.A_off=self.gpu_layer_A.output_offset
        self.B_off=self.gpu_layer_B.output_offset

        