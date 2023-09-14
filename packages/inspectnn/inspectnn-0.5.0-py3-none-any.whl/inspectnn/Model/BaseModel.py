import time,sys,imp,os
#import pandas 
from numba import cuda, jit
import numpy as np

from inspectnn.Conv.ConvLayer import ConvLayer
from inspectnn.Dense.DenseLayer import DenseLayer

class Multiply():
    def __init__(self,m,Area,Power,name="Exact"):
        self.multiplier = m
        self.Power = Power/65536.0#per moltiplicazione
        self.Area  = Area
        self.name = name

class BaseModel():
    def __init__(self, multiplier,quant_nbits = 8,input_shape=[28, 28, 1],save_csv_path=''):
        
        self.quant_nbits = quant_nbits
        self.input_shape = input_shape
        self.elapsed_time = 0
        self.total_elapsed_time=0
        self.save_csv_path=save_csv_path
        self.images_on_gpu = False

        self.layer_apx = None
        
        if None != multiplier:
            self.exact_multiplier = multiplier
        else:#Moltiplicatore di base
            dim = 128
           
            self.def_multiplier_8b = np.zeros((2*dim,2*dim),dtype=int)
            self.def_multiplier_7b = np.zeros((2*dim,2*dim),dtype=int)
            self.def_multiplier_6b = np.zeros((2*dim,2*dim),dtype=int)
            self.def_multiplier_5b = np.zeros((2*dim,2*dim),dtype=int)
            self.def_multiplier_4b = np.zeros((2*dim,2*dim),dtype=int)
            self.def_multiplier_3b = np.zeros((2*dim,2*dim),dtype=int)
            self.def_multiplier_2b = np.zeros((2*dim,2*dim),dtype=int)
            for i in range(-dim,dim):
                for j in range(-dim,dim):
                    self.def_multiplier_8b[i+dim,j+dim]=i*j
                    self.def_multiplier_7b[i+dim,j+dim]=i*j & 0xFFFD  
                    self.def_multiplier_6b[i+dim,j+dim]=i*j & 0xFFFB  
                    self.def_multiplier_5b[i+dim,j+dim]=i*j & 0xFFF9  
                    self.def_multiplier_4b[i+dim,j+dim]=(i*j) & 0xFFF7  
                    self.def_multiplier_3b[i+dim,j+dim]=(i*j) & 0xFFF5  
                    self.def_multiplier_2b[i+dim,j+dim]=(i*j) & 0xFFF3  
            
            self.exact_multiplier = Multiply(cuda.to_device(self.def_multiplier_8b),729.8,0.425)
            
            self.def_multiplier_8b = Multiply(cuda.to_device(self.def_multiplier_8b),800,0.410,"8b")
            self.def_multiplier_7b = Multiply(cuda.to_device(self.def_multiplier_7b),600,0.300,"7b")
            self.def_multiplier_6b = Multiply(cuda.to_device(self.def_multiplier_6b),400,0.200,"6b")
            self.def_multiplier_5b = Multiply(cuda.to_device(self.def_multiplier_5b),350,0.125,"5b")
            self.def_multiplier_4b = Multiply(cuda.to_device(self.def_multiplier_4b),200,0.100,"4b")
            self.def_multiplier_3b = Multiply(cuda.to_device(self.def_multiplier_3b),100,0.050,"3b")
            self.def_multiplier_2b = Multiply(cuda.to_device(self.def_multiplier_2b),50 ,0.025,"2b")

        self.all_multiplier_quant = [self.def_multiplier_2b,self.def_multiplier_3b,self.def_multiplier_4b,self.def_multiplier_5b,self.def_multiplier_6b,self.def_multiplier_7b,self.def_multiplier_8b]
        self.net = None

   
    def evaluate(self,images,labels,log=False,reset_statistics=False):
        if reset_statistics:
            for id_layer in range(len(self.net.layers)):
                self.net.elapsed_time[id_layer] = 0
                
        
        num_of_samples=len(images)
        if log : 
            print(f"Testing on {len(images)} images.")
        st = time.time()
        if self.images_on_gpu:
            Accuracy = self.net.evaluate_accuracy(self.labels, self.images)
        else:
            Accuracy = self.net.evaluate_accuracy(labels, images)
        if log :
            print(f"Accuracy: {Accuracy}")
        et = time.time()
        self.elapsed_time = et - st
        self.total_elapsed_time+=self.elapsed_time
        if log :
            print('MIMT execution time:', self.elapsed_time, 'seconds')
            print('FPS:', num_of_samples/self.elapsed_time) 
            self.net.print_time_statics()
        return Accuracy
    
    def evaluate_pure(self):

        st = time.time()
        
        #Accuracy = self.net.evaluate_accuracy(self.labels, self.images)
        Accuracy = self.net.evaluate_accuracy(self.labels, self.images) #TODO ulteriori esperimenti da fare, da sostituire con la versione avanzata con la sensitivita

        et = time.time()
        self.elapsed_time = et - st
        self.total_elapsed_time+=self.elapsed_time

        return Accuracy
    
    def evaluate_pure_AdversialAttack(self):

        st = time.time()
        
        #Accuracy = self.net.evaluate_accuracy(self.labels, self.images)
        Accuracy = self.net.evaluate_accuracy(self.AdversialAttack.labels, self.AdversialAttack.images) #TODO ulteriori esperimenti da fare, da sostituire con la versione avanzata con la sensitivita

        et = time.time()
        self.elapsed_time = et - st
        self.total_elapsed_time+=self.elapsed_time

        return Accuracy
    
    def evaluate_baseline_accuracy(self,images_apx,labels_apx,reset_statistics=False):
        self.net.update_multipler([self.exact_multiplier])
    
        self.baseline_accuracy = self.evaluate(images_apx, labels_apx,reset_statistics=reset_statistics)

    def evaluate_all(self,images_apx,labels_apx,print_results=False):
        results = []
        id = 0
        for multiplier in self.all_multiplier:
   
            self.net.update_multipler([multiplier])
            accuracy = self.evaluate(images_apx, labels_apx)
            Power = self.net.return_Power()
            results.append([multiplier.name, Power,accuracy, self.baseline_accuracy - accuracy, self.elapsed_time])
            if print_results:
                print(f"{id}/{len(self.all_multiplier):}" ,results[-1])

            id+=1
        return results
    
    def load_all_multiply_for_layer(self,configuration):
        self.all_multiplier = []
        net = self.net
        
        idx=0
        vector_list_mul_data = configuration["axmuls"]
        
        data_model = None
        for  list_mul_data in vector_list_mul_data:

            for mul_data in list_mul_data:
                multiplier, _ = self._load_multiplier(mul_data["path"])
                multiplier.name=mul_data["name"]
                
                multiplier.MAE   =mul_data['MAE']
                multiplier.AWCE  =mul_data['AWCE']
                multiplier.MRE   =mul_data['MRE']
                multiplier.Power =mul_data['power']/65536.0#per moltiplicazione
                multiplier.Area  =mul_data['area']
    
                if data_model is None:
                    data_model = [multiplier.model]
                else:
                    data_model = np.concatenate((data_model,[multiplier.model]))

                self.all_multiplier.append(multiplier)
                
        
        self.all_multiplier_gpu = cuda.to_device(np.array(data_model,dtype=np.int16))

        self.net.load_total_multiply_gpu(self.all_multiplier_gpu)

        return self.all_multiplier, data_model

    def load_all_multiply(self,approxmults_path,filter=None):
        self.all_multiplier = []
        
        for root, dirs, files in os.walk(approxmults_path):
            for f in files:
                if f.endswith('.py') and ((filter is not None and filter in f) or filter is None):
                    py_filename = os.path.join(root, f)
                    multiplier, _ = self._load_multiplier(py_filename)
                    multiplier.filename=py_filename.split('/')[-2]
                    self.all_multiplier.append(multiplier)
        
        return self.all_multiplier
                   
    
    def _import_module(self,module_name):
        # Fast path: see if the module has already been imported.
        try:
            return sys.modules[module_name]
        except KeyError:
            pass
        # If any of the following calls raises an exception,
        # there's a problem we can't handle -- let the caller handle it.
        fp, pathname, description = imp.find_module(module_name)
        try:
            return imp.load_module(module_name, fp, pathname, description)    
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()


    def _load_multiplier(self,filename):
        module_name = os.path.basename(filename)
        name_class = os.path.splitext(module_name)[0]
        name_import = os.path.splitext(filename)[0]
        module_name = self._import_module(name_import)
        variant_mul = getattr(module_name, name_class)
        mult_class = variant_mul()
        mult_class.multiplier = cuda.to_device(np.array(mult_class.model,dtype=int))
        return mult_class, name_class
    

    def load_img_gpu(self,images,labels):
        self.images_on_gpu=True
        self.labels = labels
        self.images = []
        for i in range(len(images)):
            self.images.append(cuda.to_device(np.ascontiguousarray(images[i], dtype=np.int32)))
            
            
    def load_AdversialAttack_img_gpu(self,images,labels):
        class AdversialAttack():
            def __init__(self,images,labels):
                self.labels = [] 
                self.images = []
                for i in range(len(images)):
                    self.images.append(cuda.to_device(np.ascontiguousarray(images[i], dtype=np.int32)))
                    self.labels.append(labels[i])
                    
        self.AdversialAttack = AdversialAttack(images,labels)
       

    def load_img_quantizate_on_gpu(self,images,labels):
        self.images_on_gpu=True
        self.labels = labels
        self.images = []
        
        for i in range(len(images)):
            self.net.layers[0].forward_pass(inputv = images[i])
            self.images.append(cuda.to_device(np.ascontiguousarray(self.net.layers[0].results.copy_to_host())))

        self.net.init_quantizate = False

    def generate_multipler_list(self,id,mul=None):
        #print(id)
        if mul is None:
            mul = self.all_multiplier
            #mul = self.all_multiplier_quant
        multipler_list= []
        for i in id:
            multipler_list.append(mul[i])
        return multipler_list

    def evaluate_confusion_matrix(self,images_apx,labels_apx):
        assert not self.images_on_gpu, "Preload images on GPU not supported"
        return self.net.evaluate_confusion_matrix(images_apx,labels_apx)
       
    def research_hyperparameters(self):
        self.net.evaluate_accuracy(self.labels, self.images)
        
        for id_layer in range(len(self.net.layers)):
            if isinstance(self.net.layers[id_layer], (ConvLayer, DenseLayer)):
                self.net.layers[id_layer].research_hyperparameters()


    def name_multipler(self,id_mul):
        assert id_mul < len(self.all_multiplier), f"Error id_mul {id_mul} > N_layer_with_multiply {len(self.all_multiplier)}"
        return self.all_multiplier[id_mul].name
    
    
    def name_multiplers(self,id_mul):
        names=[]
        for id in id_mul:
            assert id < len(self.all_multiplier), f"Error id_mul {id} > N_layer_with_multiply {len(self.all_multiplier)}"
            names.append(self.all_multiplier[id].name)
            
        return names
    
    
    
    #Questa funzione prende in ingresso il vettore di variaibli  della ricerca e restituisce il vettore di moltiplicatori per filtri per il modello
    def generate_multipler_list_expand(self,vector_decision_var):
        N_filter = self.net.get_number_of_all_filters()
        vector_mul = np.full(N_filter,-1,dtype=int)
        k=0
        #per ogni layer
        id_decision_var = 0
        for ii in range(self.net.N_layer_with_multiply):
            while not isinstance(self.net.layers[k], (ConvLayer, DenseLayer)):
                k+=1
            
            for i in self.net.layers[k].group_filter_level_0:
                vector_mul[i] = vector_decision_var[id_decision_var]     
            
            id_decision_var += 1
            
            if len(self.net.layers[k].group_filter_level_1) > 0:
                for i in self.net.layers[k].group_filter_level_1:
                    vector_mul[i] = vector_decision_var[id_decision_var]     
                id_decision_var += 1    
            k+=1
            
        print(vector_mul)    
        return vector_mul, self.get_power(vector_decision_var,self.moltiply_for_decisoon_var)
    
    
    
    def get_power(self,list_multipliers,list_moltiplications):
        power = 0
        for idx, m in enumerate(list_multipliers):
            power += self.all_multiplier[m].Power*list_moltiplications[idx]
        return power
