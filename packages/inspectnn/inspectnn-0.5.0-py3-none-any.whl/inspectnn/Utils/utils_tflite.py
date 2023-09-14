from keras.models import load_model
import numpy as np, time, tensorflow as tf, random, os, sys
rotate_type=np.int32

def traslate(b):
    #print(b[1:])
    #bb=np.int32(b)
    c= np.concatenate(([b[-1]], b[0:-1]))
    return c

def rotate_2d(a,shape):
    
   #print("coordiante= ",traslate(a.shape))
    b = np.zeros(shape,dtype=rotate_type)
    #print(b.shape)
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            b[j,i]=a[i,j]
    return b

def rotate_3d(a,shape):
    
    b = np.zeros(shape,dtype=rotate_type)
    
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            for k in range(a.shape[2]):
                b[j,k,i]=a[i,j,k]
    return b


def rotate_4d(a,shape):
    
    b = np.zeros(shape,dtype=rotate_type)
    
    #print("shape 4",a.shape,b.shape)
    
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            for k in range(a.shape[2]):
                for z in range(a.shape[3]):
                    b[j,k,z,i]=a[i,j,k,z]
    return b



class DATA_layer:
    def __init__(self,tensore,scales,offset):
        self.tensore = tensore
        self.scales = scales
        self.offset = offset

class DATA_layer_quant:
    def __init__(self,scales,offset):
        self.scales = scales
        self.offset = offset


def load_weights_tflite(model_h5,model_tflite):
    
    model=load_model(model_h5)
    
    interpreter = tf.lite.Interpreter(model_path=model_tflite,experimental_preserve_all_tensors=True)
    interpreter.allocate_tensors()
    model.summary()
    
    id_model_layer=0
    id_tensor = 0
    j_model = 0
    data_layer=[]
    data_layer_quant=[]
    learned_parameters = []
    
    layer_not_used = np.zeros(len(interpreter.get_tensor_details()))==0
    #print(layer_not_used)
    #ricerca e associa ai layer di pesi e bias
    for j in range(len(model.weights)):
        #calcolati l' id del layer corispondente (mi serve per conoscere il nome)
        #in teoria basterebbe ciclare solo sui layer e gestire gli id di soli quellic he hanno i pesi
        while(len(model.layers[id_model_layer].get_weights())==0):id_model_layer+=1
        #print(f"{model.layers[id_model_layer].name} -- {model.layers[id_model_layer].get_weights().shape}")
        for i in range(1,len(interpreter.get_tensor_details())):
            first_name = interpreter.get_tensor_details()[i]['name'].split(';')[0]

            

            if(np.array_equal(interpreter.get_tensor_details()[i]['shape'],traslate(model.weights[j].shape))):
                
                if(model.layers[id_model_layer].name in first_name):
                    id_tensor = i
                    j_model= j
                    layer_not_used[i]=False
                    #print(layer_not_used[i],model.layers[id_model_layer].name,j,i,interpreter.get_tensor_details()[i]['name'])
                    #print("[Connect]",j," - ",i,interpreter.get_tensor_details()[i]['shape'],interpreter.get_tensor_details()[i]['name'])
                    
        
            #if(layer_not_used[i] and (model.layers[id_model_layer].name in first_name)):
            #    print(model.layers[id_model_layer].name,j,i,interpreter.get_tensor_details()[i]['name'])
            #    layer_not_used[i]=False

        #TODO: Fare funzione get_tes        
        parameter=interpreter.get_tensor(id_tensor)
       
        #print(model.weights[j_model].shape, len(interpreter.get_tensor(id_tensor).shape))
        #parameter=np.reshape(np.ascontiguousarray(interpreter.get_tensor(id_tensor)),model.weights[j_model].shape,order='A')#TODO:verificare ordine C va F da accuracy 0
        
        
        learned_parameters.append(parameter)
                                  
        data_layer.append(DATA_layer(interpreter.get_tensor(id_tensor),
                         interpreter.get_tensor_details()[id_tensor]['quantization_parameters']['scales'],
                         interpreter.get_tensor_details()[id_tensor]['quantization_parameters']['zero_points']
                        ))
        
        if(j%2 == 1):
            #devo incrementare ogni 2 weights perche un layer ha weights e bias
            id_model_layer+=1
        #print(interpreter.get_tensor_details()[id_tensor]['quantization_parameters'])
        #print(interpreter.get_tensor(id_tensor))


    id_model_layer=0
    id_tensor = 0
    for j in range(len(model.weights)):
        while(len(model.layers[id_model_layer].get_weights())==0):id_model_layer+=1
        #print(f"{model.layers[id_model_layer].name} -- {model.layers[id_model_layer].get_weights().shape}")
        for i in range(1,len(interpreter.get_tensor_details())):
            first_name = interpreter.get_tensor_details()[i]['name'].split(';')[0]
            if(layer_not_used[i] and (model.layers[id_model_layer].name in first_name)):
                #print(model.layers[id_model_layer].name,j,i,interpreter.get_tensor_details()[i]['name'])

                data_layer_quant.append(DATA_layer_quant(
                                             
                         interpreter.get_tensor_details()[i]['quantization'][0],
                         interpreter.get_tensor_details()[i]['quantization'][1]
                        ))
                layer_not_used[i]=False
    
                
        if(j%2 == 1):
            #devo incrementare ogni 2 weights perche un layer ha weights e bias
            id_model_layer+=1
        
    return    learned_parameters,data_layer,data_layer_quant,model,interpreter