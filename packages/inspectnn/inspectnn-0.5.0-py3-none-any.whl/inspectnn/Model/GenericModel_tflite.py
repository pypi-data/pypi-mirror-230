import time

import numpy as np

from inspectnn.Conv.ConvLayer_TFLITE import ConvLayer_TFLITE
from inspectnn.Dense.DenseLayer_TFLITE import DenseLayer_TFLITE
from inspectnn.Pooling.PoolingLayer_TFLITE import PoolingLayer_TFLITE
from inspectnn.Mean.MeanLayer_TFLITE import MeanLayer_TFLITE
from inspectnn.Flatten.FlattenLayer import FlattenLayer
from inspectnn.PAD.PadLayer import PadLayer
from inspectnn.Add.AddLayer import AddLayer

from inspectnn.Model.NetworkModel_tflite import NetworkModelTflite
from inspectnn.Model.BaseModel_tflite import BaseModel_tflite
from inspectnn.Quantizate.QuantizateLayer import QuantizateLayer
from inspectnn.SoftmaxLayer import SoftmaxLayer
from inspectnn.Reshape.ReshapeLayer import ReshapeLayer

import tflite
import numpy as np, time, tensorflow as tf

class GenericModelTflite(BaseModel_tflite):
    def __init__(self,path_tf_file, input_no_normalizate=True):

        self.quant_nbits = 7
        save_csv_path=''
        self.input_no_normalizate = input_no_normalizate
 
        #print("path file tflite:",path_tf_file)
        self.interpreter = tf.lite.Interpreter(model_path=path_tf_file,experimental_preserve_all_tensors=True)
        self.interpreter.allocate_tensors()
        #apri il file tflite
        f = open(path_tf_file,"rb")
        buf = f.read()

        self.model = tflite.Model.GetRootAsModel(buf,0)

        #print("len:",self.model.SubgraphsLength())
        graf = self.model.Subgraphs(0)
        input_shape = self.interpreter.get_tensor_details()[graf.Operators(0).Inputs(0)]['shape'][1:]
        super().__init__(None,self.quant_nbits,input_shape,save_csv_path)
       
        #ssuper().__init__(None,self.quant_nbits,input_shape,save_csv_path)
        layers = []
        self.data_layer = []
        self.data_layer_quant = []
        self.learned_parameters = []

        self.n_moltiplicazioni = []
        self.tensor_output_layer = []

        
        #Crea i singoli layer
        for i in range(graf.OperatorsLength()-1):#ELIMINA L'ULTIMO LAYER CHE È QUELLO DI OUTPUT
            op=graf.Operators(i)      
            op_code = self.model.OperatorCodes(op.OpcodeIndex())     
            #print(i,tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())],op.InputsLength(),op.OutputsLength())
            #for j in range(op.InputsLength()):
            #    print("\t",op.Inputs(j))
           
            layers.append(self.__ImportLayer__(op))
            
            layers[-1].id_output_layer = op.Outputs(0) #Layers id tflite
            self.tensor_output_layer.append(op.Outputs(0))
            #print(layers[-1].name,op.Outputs(0),op.Inputs(0))
            #print("OUT:",op.Outputs(0))

        #collega le uscite dei layer
        layers[0].gpu_output_memory = True
        for i in range(1,graf.OperatorsLength()-2):
            layers[i].load_input_layer(layers,self.tensor_output_layer)
        
        layers[-2].end_layer =True
        layers[-2].gpu_output_memory = False
        layers[-1].pre_layer = layers[-2]

        self.net =  NetworkModelTflite(quant_data_scale=self.data_layer_quant,
                                       quant_data=self.data_layer, 
                                       learned_parameters = self.learned_parameters, 
                                       input_shape = input_shape,
                                       layers = layers)

        #print(path_tf_file,np.sum(self.n_moltiplicazioni))

        #TODO: da controlare, dovrebbe far risparmiare un po di memoria eprche non vengono piu usati
        #del self.interpreter, self.model
        #del self.tensor_output_layer
        
        #TODO: far si che i risultati rimangono su gpu e solo alla fine di tutte le valutazioni si caricano su cpu
        
    def __LayerOpcodeConverter__(self,id):
        return self.model.OperatorCodes(id).BuiltinCode() 

    def __ReadGenericParameters__(self,op,name_id=0):
        #print(self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split(';')[-name_id])
        try:
            name_layer=self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split(';')[-name_id].split('/')[-2]
        except:
            name_layer=self.interpreter.get_tensor_details()[op.Outputs(0)]['name']
            
        input_shape = self.interpreter.get_tensor_details()[op.Inputs(0)]['shape'][1:]

        return name_layer,input_shape
    
    def __ImportLayer__(self,op):
        disponibilita_gpu=True
        #print(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())])
        #TODO: parametrizare meglio i layer prendendo i dati da op
        layer=None
        op_opt = op.BuiltinOptions()
        
        if(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "QUANTIZE"):
            
            #quantize_op = tflite.QuantizeOptions()
            #quantize_op.Init(op_opt)
            #print(quantize_op)
            
            name_layer,input_shape = self.__ReadGenericParameters__(op)
            layer = QuantizateLayer(quant_nbits =  self.quant_nbits, name = 'Q_' + name_layer)
            layer.code_tensor_inputs = [op.Inputs(i) for i in range(1)]

            if op.Inputs(0) == 0 and self.input_no_normalizate:
                quant_output_k = 1#self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]#*255
            else:
                quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]

            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]

            layer.load_weights(input_shape = input_shape,enable_gpu=disponibilita_gpu,gpu_input_memory=None,
                               quant_output_k=quant_output_k,quant_output_offset=quant_output_offset)
                
        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "CONV_2D"):
            
            conv_op = tflite.Conv2DOptions()
            conv_op.Init(op_opt.Bytes, op_opt.Pos)

            name_layer,input_shape = self.__ReadGenericParameters__(op,2)#o 1 dipende =()
            type_attivation=self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split(';')[0].split('/')[-1]

            if conv_op.Padding() == tflite.Padding.SAME :
                padding_type ='same'
            else:
                padding_type ='valid'
            
            layer = ConvLayer_TFLITE(stride = (conv_op.StrideW(), conv_op.StrideH()), padding = (0, 0), activation = type_attivation, padding_type = padding_type,
                                      quant_nbits =  self.quant_nbits, name = name_layer,multiplier=self.exact_multiplier)#multiplier=MUL_2bit_importata
           
            self.learned_parameters.append(self.interpreter.get_tensor(op.Inputs(1)))#pesi weights
            self.learned_parameters.append(self.interpreter.get_tensor(op.Inputs(2)))#pesi bias
            
            quantization_pesi = self.interpreter.get_tensor_details()[op.Inputs(1)]['quantization_parameters']['scales']
            quantization_bias = self.interpreter.get_tensor_details()[op.Inputs(2)]['quantization_parameters']['scales']

            quant_input_k = self.interpreter.get_tensor_details()[op.Inputs(0)]['quantization'][0]
            quant_input_offset =  self.interpreter.get_tensor_details()[op.Inputs(0)]['quantization'][1]

            output_shape=self.interpreter.get_tensor_details()[op.Outputs(0)]['shape'][1:]
            
            quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]
            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]
            
            layer.code_tensor_inputs = [op.Inputs(i) for i in range(1)]
            layer.load_weights(input_shape = input_shape,output_shape=output_shape, weights = self.learned_parameters[-2], biases = self.learned_parameters[-1],
                                                                        enable_gpu=disponibilita_gpu,gpu_input_memory=None,
                                                                        quant_data=quantization_pesi,quant_bias=quantization_bias,
                                                                        quant_input_k=quant_input_k,quant_input_offset=quant_input_offset,
                                                                        quant_output_k=quant_output_k,quant_output_offset=quant_output_offset
                                                                        )
            #dimensione kernel(senza il numero di filtri, presenti nel output) * dimensione output
            layer.n_moltiplicazioni=np.prod(self.interpreter.get_tensor(op.Inputs(1)).shape[1:])*np.prod(output_shape)
              
        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "FULLY_CONNECTED"):

            type_attivation=self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split(';')[1].split('/')[-1]
            name_layer,input_shape = self.__ReadGenericParameters__(op,1)
            

            if ( type_attivation != 'relu' and type_attivation != 'Relu'):
                type_attivation='softmax'
            layer=DenseLayer_TFLITE(activation = type_attivation, quant_nbits =  self.quant_nbits, name = name_layer,multiplier=self.exact_multiplier)
            self.learned_parameters.append(self.interpreter.get_tensor(op.Inputs(1)))#pesi weights

            self.learned_parameters.append(self.interpreter.get_tensor(op.Inputs(2)))#pesi bias
            
            quantization_pesi = self.interpreter.get_tensor_details()[op.Inputs(1)]['quantization_parameters']['scales']
            quantization_bias = self.interpreter.get_tensor_details()[op.Inputs(2)]['quantization_parameters']['scales']

            quant_input_k = self.interpreter.get_tensor_details()[op.Inputs(0)]['quantization'][0]
            quant_input_offset =  self.interpreter.get_tensor_details()[op.Inputs(0)]['quantization'][1]

            quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]
            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]
            output_shape=self.interpreter.get_tensor_details()[op.Outputs(0)]['shape']

            layer.code_tensor_inputs = [op.Inputs(i) for i in range(1)]

            layer.load_weights(input_shape = input_shape, output_shape=output_shape,weights = self.learned_parameters[-2], biases = self.learned_parameters[-1],
                                                                        enable_gpu=disponibilita_gpu,gpu_input_memory=None,
                                                                        quant_data=quantization_pesi,quant_bias=quantization_bias,
                                                                        quant_input_k=quant_input_k,quant_input_offset=quant_input_offset,
                                                                        quant_output_k=quant_output_k,quant_output_offset=quant_output_offset
                                                                        )
            #dimensione input * output
            layer.n_moltiplicazioni=np.prod(output_shape)*np.prod(input_shape)
        
        #TODO: unire i due pool cone la variaible letta da pool_op
        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "AVERAGE_POOL_2D"):
            name_layer,input_shape = self.__ReadGenericParameters__(op)

            pool_op = tflite.Pool2DOptions()
            pool_op.Init(op_opt.Bytes, op_opt.Pos)
            
            stride =  [pool_op.StrideW(), pool_op.StrideH()] #self.interpreter.get_tensor_details()[op.Inputs(0)]['shape'][1:3]//self.interpreter.get_tensor_details()[op.Outputs(0)]['shape'][1:3]
            pool_size = [pool_op.FilterWidth(), pool_op.FilterHeight()]#stride
            
            layer = PoolingLayer_TFLITE(stride = stride, pool_size = pool_size, pooling = "avg", name = name_layer)#TODO vare averge pool
            quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]
            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]

            layer.code_tensor_inputs = [op.Inputs(i) for i in range(1)]
            layer.load_weights(input_shape = input_shape,enable_gpu=disponibilita_gpu,gpu_input_memory=None,
                               quant_output_k=quant_output_k,quant_output_offset=quant_output_offset)

        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "MAX_POOL_2D"):
            name_layer,input_shape = self.__ReadGenericParameters__(op)
            
            pool_op = tflite.Pool2DOptions()
            pool_op.Init(op_opt.Bytes, op_opt.Pos)
            
            stride =  [pool_op.StrideW(), pool_op.StrideH()]#self.interpreter.get_tensor_details()[op.Inputs(0)]['shape'][1:3]//self.interpreter.get_tensor_details()[op.Outputs(0)]['shape'][1:3]
            pool_size = [pool_op.FilterWidth(), pool_op.FilterHeight()]#stride

            layer = PoolingLayer_TFLITE(stride = stride, pool_size =pool_size, pooling = "max", name = name_layer)

            quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]
            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]

            layer.code_tensor_inputs = [op.Inputs(i) for i in range(1)]
            layer.load_weights(input_shape = input_shape,enable_gpu=disponibilita_gpu,gpu_input_memory=None,
                               quant_output_k=quant_output_k,quant_output_offset=quant_output_offset)
        
        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "RESHAPE"):
            name_layer=self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split(';')[0].split('/')[1]
            input_shape = self.interpreter.get_tensor_details()[op.Inputs(0)]['shape'][1:]
            layer = FlattenLayer(name = name_layer)

            layer.code_tensor_inputs = [op.Inputs(i) for i in range(1)]
            layer.load_weights(input_shape = input_shape,enable_gpu=disponibilita_gpu,gpu_input_memory=None)

        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "ADD"):
            type_attivation=self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split(';')[0].split('/')[-1]
            name_layer=self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split(';')[1].split('/')[-2]

            layer = AddLayer(name = name_layer, activation = type_attivation)

            input_shape_A = self.interpreter.get_tensor_details()[op.Inputs(0)]['shape']
            input_shape_B = self.interpreter.get_tensor_details()[op.Inputs(1)]['shape']
            output_shape=self.interpreter.get_tensor_details()[op.Outputs(0)]['shape'][1:]

            quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]
            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]

            layer.code_tensor_inputs = [op.Inputs(i) for i in range(2)]
            layer.load_weights(input_shape_A = input_shape_A,input_shape_B=input_shape_B,output_shape=output_shape,
                               quant_output_k=quant_output_k,quant_output_offset=quant_output_offset,
                               enable_gpu=disponibilita_gpu,gpu_input_memory=None)

        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "SOFTMAX"):
            type_attivation=self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split(';')[0].split('/')[-1]
            name_layer=self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split('/')[-1]

            output_shape=self.interpreter.get_tensor_details()[op.Outputs(0)]['shape'][1:]

            quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]
            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]
            input_shape = self.interpreter.get_tensor_details()[op.Inputs(0)]['shape']

            layer = SoftmaxLayer(name = name_layer, activation = type_attivation)

            layer.load_weights(input_shape = input_shape,output_shape=output_shape,
                               quant_output_k=quant_output_k,quant_output_offset=quant_output_offset)

        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "PAD"):
    
            name_layer=self.interpreter.get_tensor_details()[op.Outputs(0)]['name'].split(';')[0].split('/')[1]
            input_shape = self.interpreter.get_tensor_details()[op.Inputs(0)]['shape'][1:]
            output_shape=self.interpreter.get_tensor_details()[op.Outputs(0)]['shape'][1:]
            padding_shape = self.interpreter.get_tensor_details()[op.Inputs(1)]['shape'][1:]
            
            quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]
            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]
            
            layer = PadLayer(name = name_layer)

            layer.code_tensor_inputs = [op.Inputs(i) for i in range(1)]
            layer.load_weights(input_shape = input_shape,output_shape=output_shape,enable_gpu=disponibilita_gpu,gpu_input_memory=None,
                               quant_output_k=quant_output_k,quant_output_offset=quant_output_offset
                               )
            
        #TODO: sostituire con un layer Mean piu ottimizato (ne vale la pena?)
        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "MEAN"):
            name_layer,input_shape = self.__ReadGenericParameters__(op)
            

            input_shape = self.interpreter.get_tensor_details()[op.Inputs(0)]['shape'][1:]
            
            stride =  [1, 1] #self.interpreter.get_tensor_details()[op.Inputs(0)]['shape'][1:3]//self.interpreter.get_tensor_details()[op.Outputs(0)]['shape'][1:3]
            pool_size = input_shape
            
            #layer = MeanLayer_TFLITE
            layer = PoolingLayer_TFLITE(stride = stride, pool_size = pool_size, pooling = "avg", name = name_layer)#TODO vare averge pool
            quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]
            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]

            layer.code_tensor_inputs = [op.Inputs(i) for i in range(1)]
            layer.load_weights(input_shape = input_shape,enable_gpu=disponibilita_gpu,gpu_input_memory=None,
                               quant_output_k=quant_output_k,quant_output_offset=quant_output_offset)
            
        elif(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())] == "RESIZE_NEAREST_NEIGHBOR"):
            name_layer,input_shape = self.__ReadGenericParameters__(op)
            stride =  [7, 7] #self.interpreter.get_tensor_details()[op.Inputs(0)]['shape'][1:3]//self.interpreter.get_tensor_details()[op.Outputs(0)]['shape'][1:3]
            pool_size = input_shape
            
            
            input_shape = self.interpreter.get_tensor_details()[op.Inputs(0)]['shape'][1:]
            output_shape=self.interpreter.get_tensor_details()[op.Outputs(0)]['shape'][1:]
            
            
            quant_output_k = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][0]
            quant_output_offset = self.interpreter.get_tensor_details()[op.Outputs(0)]['quantization'][1]
           
            #layer = MeanLayer_TFLITE
            layer = ReshapeLayer(name = name_layer,dim_size = stride)
            
            layer.load_weights(input_shape = input_shape,output_shape=output_shape, enable_gpu=disponibilita_gpu,gpu_input_memory=None,
                               quant_output_k=quant_output_k,quant_output_offset=quant_output_offset)
            
            layer.code_tensor_inputs = [op.Inputs(i) for i in range(1)]
        else:
            print(tflite.utils.BUILTIN_OPCODE2NAME[self.__LayerOpcodeConverter__(op.OpcodeIndex())],"Not supported")
        return layer
    
  